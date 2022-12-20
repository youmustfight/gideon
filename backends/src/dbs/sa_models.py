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
def serialize_list(models):
    return list(map(lambda model: model.serialize(), to_list(models)))

# JUNCTION TABLES

organization_case_junction = Table(
    "organization_case",
    Base.metadata,
    Column("case_id", ForeignKey("case.id"), primary_key=True),
    Column("organization_id", ForeignKey("organization.id"), primary_key=True),
)
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
    def serialize(self):
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
    cases = relationship("Case", secondary=organization_case_junction, back_populates="organizations")
    users = relationship("User", secondary=organization_user_junction, back_populates="organizations")
    writing_templates = relationship("Writing", back_populates="organization")
    def serialize(self, serialize_relationships):
        cases = None
        users = None
        writing_templates = None
        # This shit breaks if we serialize a model without values
        if 'cases' in serialize_relationships:
            cases = serialize_list(self.cases)
        if 'users' in serialize_relationships:
            users = serialize_list(self.users)
        if 'writing_templates' in serialize_relationships:
            writing_templates = serialize_list(self.writing_templates)
        return {
            "id": self.id,
            "name": self.name,
            "cases": cases,
            "users": users,
            "writing_templates": writing_templates,
        }

class Case(BaseModel):
    __tablename__ = "case"
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    name = Column(Text())
    organizations = relationship("Organization", secondary=organization_case_junction, back_populates="cases")
    users = relationship("User", secondary=case_user_junction, back_populates="cases")
    documents = relationship("Document", back_populates="case")
    embeddings = relationship("Embedding", back_populates="case")
    writings = relationship("Writing", back_populates="case")
    legal_brief_facts = relationship("LegalBriefFact", back_populates="case")
    ai_action_locks = relationship("AIActionLock", back_populates="case")
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            # "organizations": list(map(lambda org: org.serialize(), to_list(self.organizations))),
            # "users": list(map(lambda user: user.serialize(), to_list(self.users))),
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
    created_at = Column(DateTime(timezone=True))

class Document(BaseModel):
    __tablename__ = "document"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    case_id = Column(Integer, ForeignKey("case.id"))
    case = relationship("Case", back_populates="documents")
    name = Column(Text())
    type = Column(String()) # pdf, image, audio, video (derive search modalities from this)
    # --- O>M for files
    status_processing_files = Column(String()) # queued, processing, completed, error
    status_processing_content = Column(String()) # queued, processing, completed, error
    files = relationship("File", back_populates="document")
    # --- content
    content = relationship("DocumentContent", back_populates="document")
    # --- content -> embeddings
    status_processing_embeddings = Column(String()) # queued, processing, completed, error
    embeddings = relationship("Embedding", back_populates="document")
    # --- content -> extracted summaries/details
    status_processing_extractions = Column(String()) # queued, processing, completed, error
    document_description = Column(Text())
    document_events = Column(JSON)
    document_summary = Column(Text())
    document_summary_one_liner = Column(Text())
    # TEMPORARY for citing slavery experiment
    document_citing_slavery_summary = Column(Text()) 
    document_citing_slavery_summary_one_liner = Column(Text()) 
    def serialize(self):
        return {
            "id": self.id,
            "case_id": self.case_id,
            "name": self.name,
            "type": self.type,
            "status_processing_files": self.status_processing_files,
            "status_processing_content": self.status_processing_content,
            "status_processing_embeddings": self.status_processing_embeddings,
            "status_processing_extractions": self.status_processing_extractions,
            "document_description": self.document_description,
            "document_events": self.document_events,
            "document_summary": self.document_summary,
            "document_summary_one_liner": self.document_summary_one_liner,
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
    def serialize(self):
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

class Embedding(BaseModel):
    __tablename__ = "embedding"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    # --- relations
    case_id = Column(Integer, ForeignKey("case.id"))
    case = relationship("Case", back_populates="embeddings")
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
    def serialize(self):
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
    def serialize(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "filename": self.filename,
            "mime_type": self.mime_type,
            "upload_key": self.upload_key,
            "upload_url": self.upload_url,
            "upload_thumbnail_url": self.upload_thumbnail_url,
        }

class LegalBriefFact(BaseModel):
    __tablename__ = "legal_brief_fact"
    id = Column(Integer, primary_key=True)
    case_id = Column(Integer, ForeignKey("case.id"))
    case = relationship("Case", back_populates="legal_brief_facts")
    text = Column(Text())
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    def serialize(self):
        return {
            "id": self.id,
            "case_id": self.case_id,
            "text": self.text,
            "created_at": self.created_at.isoformat() if self.created_at != None else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at != None else None,
        }

class Writing(BaseModel):
    __tablename__ = "writing"
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime(timezone=True))
    updated_at = Column(DateTime(timezone=True))
    case_id = Column(Integer, ForeignKey("case.id"))
    case = relationship("Case", back_populates="writings")
    organization_id = Column(Integer, ForeignKey("organization.id"))
    organization = relationship("Organization", back_populates="writing_templates")
    embeddings = relationship("Embedding", back_populates="writing")
    name = Column(Text())
    is_template = Column(Boolean())
    body_html = Column(Text())
    body_text = Column(Text())
    generated_body_html = Column(Text())
    generated_body_text = Column(Text())
    forked_writing_id = Column(Integer, ForeignKey("writing.id"))
    def serialize(self):
        return {
            "id": self.id,
            "case_id": self.case_id,
            "organization_id": self.organization_id,
            "is_template": self.is_template,
            "name": self.name,
            "body_html": self.body_html,
            "body_text": self.body_text,
        }


# CAP
class CAPCaseLaw(BaseModel):
    __tablename__ = "cap_caselaw"
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
    # extras
    document_summary = Column(Text())
    document_summary_one_liner = Column(Text())
    document_citing_slavery_summary = Column(Text())
    document_citing_slavery_summary_one_liner = Column(Text())
