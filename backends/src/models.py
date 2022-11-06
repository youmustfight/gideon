from pydash import to_list
from sqlalchemy import Column, Integer, ForeignKey, String, Table, Text
from sqlalchemy.orm import declarative_base, relationship


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
    name = Column(Text())
    email = Column(Text())
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
    organizations = relationship("Organization", secondary=organization_case_junction, back_populates="cases")
    users = relationship("User", secondary=case_user_junction, back_populates="cases")
    def serialize(self):
        return {
            "id": self.id,
            # "organizations": list(map(lambda org: org.serialize(), to_list(self.organizations))),
            # "users": list(map(lambda user: user.serialize(), to_list(self.users))),
        }

class Organization(BaseModel):
    __tablename__ = "organization"
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
    # --- O>M for files
    status_processing_files = Column(String()) # queued, processing, completed, error
    files = relationship("File", back_populates="document")
    # --- content
    content = relationship("DocumentContent", back_populates="document")
    # --- content -> embeddings
    status_processing_embeddings = Column(String()) # queued, processing, completed, error
    embeddings = relationship("Embedding", back_populates="document")
    # --- extracted summaries/details
    document_description = Column(Text())
    document_summary = Column(Text())

class DocumentContent(BaseModel):
    __tablename__ = "documentcontent"
    document_id = Column(Integer, ForeignKey("document.id"))
    document = relationship("Document", back_populates="content")
    embedding = relationship("Embedding", back_populates="document_content")
    # --- pdfs
    text = Column(Text())
    tokenizing_strategy = Column(String())
    page_number = Column(String())
    # --- audio
    # TODO: time_start
    # TODO: time_end
    # --- pdfs + video?
    # TODO: image (file reltaion?)

class Embedding(BaseModel):
    __tablename__ = "embedding"
    document_id = Column(Integer, ForeignKey("document.id"))
    document = relationship("Document", back_populates="embeddings")
    document_content_id = Column(Integer, ForeignKey("documentcontent.id"))
    document_content = relationship("DocumentContent", back_populates="embedding")
    # --- encoding model/engine info
    encoded_model = Column(Text()) # gpt3, clip
    encoded_model_engine = Column(Text()) # text-davinci-002 or text-similarity-davinci-001 vs. ViT-B/32 or ViT-L/14@336
    # --- pre-encoding
    encoding_strategy = Column(Text()) # image, text, page, minute, nsentence, sentence, ngram, user_request_question
    text = Column(Text())
    # TODO: image?
    # --- post-encoding
    npy_url = Column(Text()) # save npy binary to S3 if we need to load later (seems better for storage than storing in the sql database as a byte-array)

class File(BaseModel):
    __tablename__ = "file"
    document_id = Column(Integer, ForeignKey("document.id"))
    document = relationship("Document", back_populates="files")
    # ex: a 38 page PDF gets associated w/ the base document
    # embedding_id = fields.OneToOneRelation(Document) # ex: each page of the PDF gets associated w/ an embedding 
    # --- file props
    filename = Column(Text())
    mime_type = Column(Text())
    upload_key = Column(Text())
    upload_url = Column(Text())
    upload_thumbnail_url = Column(Text())
