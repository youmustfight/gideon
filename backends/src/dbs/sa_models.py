from pydash import to_list
from sqlalchemy import JSON, Column, DateTime, Integer, ForeignKey, String, Table, Text
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

class Case(BaseModel):
    __tablename__ = "case"
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True)
    name = Column(Text())
    organizations = relationship("Organization", secondary=organization_case_junction, back_populates="cases")
    users = relationship("User", secondary=case_user_junction, back_populates="cases")
    documents = relationship("Document", back_populates="case")
    ai_action_locks = relationship("AIActionLock", back_populates="case")
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            # "organizations": list(map(lambda org: org.serialize(), to_list(self.organizations))),
            # "users": list(map(lambda user: user.serialize(), to_list(self.users))),
        }

class Organization(BaseModel):
    __tablename__ = "organization"
    id = Column(Integer, primary_key=True)
    name = Column(Text())
    cases = relationship("Case", secondary=organization_case_junction, back_populates="organizations")
    users = relationship("User", secondary=organization_user_junction, back_populates="organizations")
    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            # "cases": list(map(lambda cse: cse.serialize(), to_list(self.cases))),
            # "users": list(map(lambda user: user.serialize(), to_list(self.users))),
        }

class Document(BaseModel):
    __tablename__ = "document"
    id = Column(Integer, primary_key=True)
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
    __tablename__ = "documentcontent"
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
    patch_size = Column(Integer)
    # --- audio/video
    start_second = Column(Integer)
    end_second = Column(Integer)
    def serialize(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "text": self.text,
            "tokenizing_strategy": self.tokenizing_strategy,
            "page_number": self.page_number,
            "start_second": self.start_second,
            "end_second": self.end_second,
        }

class Embedding(BaseModel):
    __tablename__ = "embedding"
    id = Column(Integer, primary_key=True)
    document_id = Column(Integer, ForeignKey("document.id"))
    document = relationship("Document", back_populates="embeddings")
    document_content_id = Column(Integer, ForeignKey("documentcontent.id"))
    document_content = relationship("DocumentContent", back_populates="embedding")
    # --- encoding model/engine info
    encoded_model_type = Column(Text()) # gpt3, clip
    encoded_model_engine = Column(Text()) # text-davinci-002 or text-similarity-davinci-001 vs. ViT-B/32 or ViT-L/14@336
    encoding_strategy = Column(Text()) # image, text, page, minute, nsentence, sentence, ngram, user_request_question
    # --- post-encoding
    vector_dimensions=Column(Integer())
    vector_json=Column(JSONB) # for storing raw values to easily access later
    npy_url = Column(Text()) # save npy binary to S3? probably unnecessary so now doing vector_json
    def serialize(self):
        return {
            "id": self.id,
            "document_id": self.document_id,
            "document_content_id": self.document_content_id,
            "encoded_model_type": self.encoded_model_type,
            "encoded_model_engine": self.encoded_model_engine,
            "encoding_strategy": self.encoding_strategy,
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

class AIActionLock(BaseModel):
    __tablename__ = "ai_action_lock"
    action = Column(Text())
    model_name = Column(Text())
    params = Column(JSON())
    case_id = Column(Integer, ForeignKey('case.id'))
    case = relationship("Case", back_populates="ai_action_locks")
    created_at = Column(DateTime(timezone=True))
