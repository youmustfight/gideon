from pydash import to_list
from sqlalchemy import JSON, Boolean, Column, DateTime, Integer, ForeignKey, String, Table, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID
import uuid

# BASE SETUP

Base = declarative_base()

class BaseModel(Base):
    __abstract__ = True
    id = Column(Integer(), primary_key=True)

# helper func to run serialize on a list of models
def serialize_list(models, serialize_relationships=[]):
    return list(map(lambda model: model.serialize(serialize_relationships), to_list(models)))

# JUNCTION TABLES

organization_user_junction = Table(
    "organization_user",
    Base.metadata,
    Column("user_id", ForeignKey("user.id"), primary_key=True),
    Column("organization_id", ForeignKey("organization.id"), primary_key=True),
)

case_user_junction = Table(
    "case_user",
    Base.metadata,
    Column("case_id", ForeignKey("case.id"), primary_key=True),
    Column("user_id", ForeignKey("user.id"), primary_key=True),
)

# MODEL TABLES

class User(BaseModel):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True)
    name = Column(Text())
    email = Column(Text())
    password = Column(Text())
    created_at = Column(DateTime(timezone=True))
    cases = relationship("Case", secondary=case_user_junction, back_populates="users")
    organizations = relationship("Organization", secondary=organization_user_junction, back_populates="users")
    documents = relationship("Document", back_populates="user")
    writings = relationship("Writing", back_populates="user")
    ai_action_locks = relationship("AIActionLock", back_populates="user")
    def serialize(self, serialize_relationships=[]):
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            # "cases": list(map(lambda cse: cse.serialize(), to_list(self.cases))),
            # "organizations": list(map(lambda org: org.serialize(), to_list(self.organizations))),
        }

class Organization(BaseModel):
    __tablename__ = "organization"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    name = Column(Text())
    cases = relationship("Case", back_populates="organization")
    documents = relationship("Document", back_populates="organization")
    users = relationship("User", secondary=organization_user_junction, back_populates="organizations")
    writings = relationship("Writing", back_populates="organization")
    ai_action_locks = relationship("AIActionLock", back_populates="organization")
    def serialize(self, serialize_relationships=[]):
        cases = None
        users = None
        writings = None
        # This shit breaks if we serialize a model without values
        if 'cases' in serialize_relationships:
            cases = serialize_list(self.cases)
        if 'users' in serialize_relationships:
            users = serialize_list(self.users)
        if 'writings' in serialize_relationships:
            writings = serialize_list(self.writings)
        return {
            "id": self.id,
            "name": self.name,
            "cases": cases,
            "users": users,
            "writings": writings,
        }

class Case(BaseModel):
    __tablename__ = "case"
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    name = Column(Text())
    organization_id = Column(Integer, ForeignKey("organization.id"))
    organization = relationship("Organization", back_populates="cases")
    users = relationship("User", secondary=case_user_junction, back_populates="cases")
    documents = relationship("Document", back_populates="case")
    embeddings = relationship("Embedding", back_populates="case")
    writings = relationship("Writing", back_populates="case")
    brief = relationship("Brief", back_populates="case")
    ai_action_locks = relationship("AIActionLock", back_populates="case")
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    def serialize(self, serialize_relationships=[]):
        users = None
        if 'users' in serialize_relationships:
            users = serialize_list(self.users)
        return {
            "id": self.id,
            "name": self.name,
            "organization_id": self.organization_id,
            "users": users,
        }

class AIActionLock(BaseModel):
    __tablename__ = "ai_action_lock"
    action = Column(Text())
    model_name = Column(Text())
    index_id = Column(Text())
    index_partition_id = Column(Text())
    params = Column(JSON()) # DEPRECATE
    case_id = Column(Integer, ForeignKey('case.id'))
    case = relationship("Case", back_populates="ai_action_locks")
    organization_id = Column(Integer, ForeignKey('organization.id'))
    organization = relationship("Organization", back_populates="ai_action_locks")
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship("User", back_populates="ai_action_locks")
    created_at = Column(DateTime(timezone=True))

class Document(BaseModel):
    __tablename__ = "document"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    # --- user/org/case relations
    case_id = Column(Integer, ForeignKey("case.id"))
    case = relationship("Case", back_populates="documents")
    organization_id = Column(Integer, ForeignKey("organization.id"))
    organization = relationship("Organization", back_populates="documents")
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="documents")
    # --- name
    name = Column(Text())
    type = Column(String()) # audio, docx, image, pdf, video (derive search modalities from this)
    # --- O>M for files
    status_processing_files = Column(String()) # queued, processing, completed, error
    status_processing_content = Column(String()) # queued, processing, completed, error
    files = relationship("File", back_populates="document")
    # --- content
    content = relationship("DocumentContent", back_populates="document")
    writings = relationship("Writing", back_populates="document")
    # --- content -> embeddings
    status_processing_embeddings = Column(String()) # queued, processing, completed, error
    embeddings = relationship("Embedding", back_populates="document")
    # --- content -> extracted summaries/details
    status_processing_extractions = Column(String()) # queued, processing, completed, error
    generated_description = Column(Text())
    generated_events = Column(JSON)
    generated_summary = Column(Text())
    generated_summary_one_liner = Column(Text())
    def serialize(self, serialize_relationships=[]):
        return {
            "id": self.id,
            "case_id": self.case_id,
            "organization_id": self.organization_id,
            "user_id": self.user_id,
            "name": self.name,
            "type": self.type,
            "status_processing_files": self.status_processing_files,
            "status_processing_content": self.status_processing_content,
            "status_processing_embeddings": self.status_processing_embeddings,
            "status_processing_extractions": self.status_processing_extractions,
            "generated_description": self.generated_description,
            "generated_events": self.generated_events,
            "generated_summary": self.generated_summary,
            "generated_summary_one_liner": self.generated_summary_one_liner,
        }

class DocumentContent(BaseModel):
    __tablename__ = "document_content"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("document.id"))
    document = relationship("Document", back_populates="content")
    embedding = relationship("Embedding", back_populates="document_content")
    # --- pdfs
    text = Column(Text())
    tokenizing_strategy = Column(String())
    page_number = Column(String())
    sentence_number = Column(Integer())
    sentence_start = Column(Integer())
    sentence_end = Column(Integer())
    # --- image
    image_file_id = Column(Integer, ForeignKey("file.id"))
    image_file = relationship("File", back_populates="document_content_image_file")
    image_patch_size = Column(Integer)
    # --- audio/video
    second_start = Column(Integer)
    second_end = Column(Integer)
    def serialize(self, serialize_relationships=[]):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "text": self.text,
            "tokenizing_strategy": self.tokenizing_strategy,
            "page_number": self.page_number,
            "sentence_number": self.sentence_number,
            "sentence_start": self.sentence_start,
            "sentence_end": self.sentence_end,
            "second_start": self.second_start,
            "second_end": self.second_end,
        }

class File(BaseModel):
    __tablename__ = "file"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("document.id"))
    document = relationship("Document", back_populates="files")
    document_content_image_file = relationship("DocumentContent", back_populates="image_file")
    # ex: a 38 page PDF gets associated w/ the base document
    # embedding_id = fields.OneToOneRelation(Document) # ex: each page of the PDF gets associated w/ an embedding 
    # --- file props
    filename = Column(Text())
    mime_type = Column(Text())
    upload_key = Column(Text())
    upload_url = Column(Text())
    upload_thumbnail_url = Column(Text())
    def serialize(self, serialize_relationships=[]):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "filename": self.filename,
            "mime_type": self.mime_type,
            "upload_key": self.upload_key,
            "upload_url": self.upload_url,
            "upload_thumbnail_url": self.upload_thumbnail_url,
        }

class Brief(BaseModel):
    __tablename__ = "brief"
    id = Column(Integer, primary_key=True)
    # relations
    case_id = Column(Integer, ForeignKey("case.id"))
    case = relationship("Case", back_populates="brief")
    cap_case_id = Column(Integer, ForeignKey("cap_case.id"))
    cap_case = relationship("CAPCaseLaw", back_populates="brief")
    # properties
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    # case law + case brief (both use facts and issues, but case law briefs won't have holding/reasoning yet since that's from the judge)
    facts = Column(JSONB()) # { text, type = "matter" | "judgment" | "fact" | "procedure" ? }[] # (name of the case and its parties, what happened factually and procedurally, and the judgment)
    issues = Column(JSONB()) # { issue, holding, reasoning }[] # (what is in dispute, the applied rule of law, reasons for the holding)
    # --- issue ('Whether ...') may be more than 1
    # --- TODO: related_facts ??? (how do we associate issues w/ facts? should we? or do we keep it loose)
    # --- holding (court/judge decision. Yes/No in response to issue)
    # --- TODO: rule? (what is the rule being applied to the facts?)
    # --- reasoning (combines facts w/ rule of law. court states whether arguments are sound)
    # conclusion (court affirms/reversed if appealate)
    # TODO: appellite brief? such as the courts a decision has gone through?
    def serialize(self, serialize_relationships=[]):
        return {
            'id': self.id,
            'cap_case_id': self.cap_case_id,
            'case_id': self.case_id,
            'created_at': str(self.created_at),
            'updated_at': str(self.updated_at),
            'facts': self.facts,
            'issues': self.issues,
        }

class Writing(BaseModel):
    __tablename__ = "writing"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    type = Column(Text())
    name = Column(Text())
    is_template = Column(Boolean())
    body_html = Column(Text())
    body_text = Column(Text())
    generated_body_html = Column(Text())
    generated_body_text = Column(Text())
    forked_writing_id = Column(Integer, ForeignKey("writing.id"))
    # relations
    case_id = Column(Integer, ForeignKey("case.id"))
    case = relationship("Case", back_populates="writings")
    document_id = Column(Integer, ForeignKey("document.id"))
    document = relationship("Document", back_populates="writings")
    organization_id = Column(Integer, ForeignKey("organization.id"))
    organization = relationship("Organization", back_populates="writings")
    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship("User", back_populates="writings")
    embeddings = relationship("Embedding", back_populates="writing")
    def serialize(self, serialize_relationships=[]):
        return {
            "id": self.id,
            "case_id": self.case_id,
            "document_id": self.document_id,
            "organization_id": self.organization_id,
            "user_id": self.user_id,
            "is_template": self.is_template,
            "name": self.name,
            "body_html": self.body_html,
            "body_text": self.body_text,
        }


# CAP
class CAPCaseLaw(BaseModel):
    __tablename__ = "cap_case"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    cap_id = Column(Integer()) # maps just bad to their "id"
    url = Column(Text())
    name = Column(Text())
    name_abbreviation = Column(Text())
    decision_date = Column(Text())
    docket_number = Column(Text())
    first_page = Column(Text())
    last_page = Column(Text())
    citations = Column(JSON()) # { type: String, cite: String }[]
    volume = Column(JSON()) # { url, volume_number, barcode }
    reporter = Column(JSON()) # { url, full_name, id }
    court = Column(JSON()) # { url, name_abbreviation, slug, id, name }
    jurisdiction = Column(JSON()) # { id, name_long, url, slug, whitelisted: boolean, name }
    cites_to = Column(JSON()) # { cite: string (ex: "10 Mass. 199"), category: string (ex: "reporters:state"), reporter: string (ex: "Mass"), case_ids: number[], opinion_id: number }[]
    frontend_url = Column(Text())
    frontend_pdf_url = Column(Text())
    preview = Column(JSON()) # ?[]
    analysis = Column(JSON()) # { cardinality, char_count, ocr_confidence, pagerank, sha256, simhash, word_count, random_id, random_bucket }
    last_updated = Column(Text())
    provenance = Column(JSON()) # { date_added: string (ex: "2022-01-01"), source: string, batch: string }
    casebody = Column(JSON()) # { status, judges: string[], parties: string[], opinions: { text, type, author }[], attorneys: string[], corrections, head_matter }
    # statuses
    status_processing_content = Column(Text()) # queued, processing, completed, error
    status_processing_embeddings = Column(Text()) # queued, processing, completed, error
    status_processing_extractions = Column(Text()) # queued, processing, completed, error
    # extras
    project_tag = Column(Text()) # ex: citing_slavery (for search filtering later)
    generated_summary = Column(Text())
    generated_summary_one_liner = Column(Text())
    generated_citing_slavery_summary = Column(Text())
    generated_citing_slavery_summary_one_liner = Column(Text())
    # relations to
    brief = relationship("Brief", back_populates="cap_case")
    cap_case_content = relationship("CAPCaseLawContent", back_populates="cap_case")
    embeddings = relationship("Embedding", back_populates="cap_case")
    def serialize(self, serialize_relationships=[]):
        return {
            "id": self.id,
            'cap_id': self.cap_id,
            'url': self.url,
            'name': self.name,
            'name_abbreviation': self.name_abbreviation,
            'decision_date': self.decision_date,
            'docket_number': self.docket_number,
            'first_page': self.first_page,
            'last_page': self.last_page,
            'citations': self.citations,
            'volume': self.volume,
            'reporter': self.reporter,
            'court': self.court,
            'jurisdiction': self.jurisdiction,
            'cites_to': self.cites_to,
            'frontend_url': self.frontend_url,
            'frontend_pdf_url': self.frontend_pdf_url,
            'preview': self.preview,
            'analysis': self.analysis,
            'last_updated': self.last_updated,
            'provenance': self.provenance,
            'casebody': self.casebody,
            # extras
            'project_tag': self.project_tag,
            'generated_summary': self.generated_summary,
            'generated_summary_one_liner': self.generated_summary_one_liner,
            'generated_citing_slavery_summary': self.generated_citing_slavery_summary,
            'generated_citing_slavery_summary_one_liner': self.generated_citing_slavery_summary_one_liner,
        }

class CAPCaseLawContent(BaseModel):
    __tablename__ = "cap_case_content"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    # --- general
    type = Column(Text()) # head_matter, opinion_majority_paragraph, opinion_minority_paragraph, ???
    text = Column(Text())
    # --- head_matter ?
    # --- opinion
    paragraph_number = Column(Integer())
    # --- relations
    cap_case_id = Column(Integer, ForeignKey("cap_case.id"))
    cap_case = relationship("CAPCaseLaw", back_populates="cap_case_content")
    embedding = relationship("Embedding", back_populates="cap_case_content")
    def serialize(self, serialize_relationships=[]):
        return {
            "id": self.id,
            "cap_case_id": self.cap_case_id,
            "type": self.type,
            "text": self.text,
            "paragraph_number": self.paragraph_number,
        }

class Embedding(BaseModel):
    __tablename__ = "embedding"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    # --- relations
    case_id = Column(Integer, ForeignKey("case.id"))
    case = relationship("Case", back_populates="embeddings")
    cap_case_id = Column(Integer, ForeignKey("cap_case.id"))
    cap_case = relationship("CAPCaseLaw", back_populates="embeddings")
    cap_case_content_id = Column(Integer, ForeignKey("cap_case_content.id"))
    cap_case_content = relationship("CAPCaseLawContent", back_populates="embedding")
    document_id = Column(Integer, ForeignKey("document.id"))
    document = relationship("Document", back_populates="embeddings")
    document_content_id = Column(Integer, ForeignKey("document_content.id"))
    document_content = relationship("DocumentContent", back_populates="embedding")
    writing_id = Column(Integer, ForeignKey("writing.id"))
    writing = relationship("Writing", back_populates="embeddings")
    # --- encoding model/engine info
    encoded_model_type = Column(Text()) # DEPRECATED: gpt3, clip
    encoded_model_engine = Column(Text()) # text-davinci-002 or text-similarity-davinci-001 vs. ViT-B/32 or ViT-L/14@336
    encoding_strategy = Column(Text()) # image, text, page, minute, nsentence, sentence, ngram
    # --- post-encoding/index
    ai_action = Column(Text()) # enum value
    index_id = Column(Text()) # aka Pinecone DB index id
    index_partition_id = Column(Text()) # aka Pinecone DB namespace
    indexed_status = Column(String()) # 'error', 'completed', 'queued'
    vector_dimensions=Column(Integer())
    vector_json=Column(JSONB) # for storing raw values to easily access later
    npy_url = Column(Text()) # DEPRECATED: save npy binary to S3? probably unnecessary so now doing vector_json
    def serialize(self, serialize_relationships=[]):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "document_content_id": self.document_content_id,
            "encoded_model_type": self.encoded_model_type,
            "encoded_model_engine": self.encoded_model_engine,
            "encoding_strategy": self.encoding_strategy,
            "ai_action": self.ai_action,
            "indexed_status": self.indexed_status,
        }

