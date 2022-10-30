from tortoise import Model, fields

class User(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField(null=True)
    email = fields.TextField(null=True)
    # --- relations
    cases = fields.ReverseRelation["Case"]
    organizations = fields.ReverseRelation["Organization"]

class Organization(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField(null=True)
    # --- relations
    cases = fields.ReverseRelation["Case"]
    users: fields.ManyToManyRelation[User] = fields.ManyToManyField(
        "models.User", related_name="organizations"
    )

class Case(Model):
    id = fields.IntField(pk=True)
    organization: fields.ForeignKeyRelation[Organization] = fields.ForeignKeyField(
        "models.Organization", related_name="cases", null=True
    )
    users: fields.ManyToManyRelation[User] = fields.ManyToManyField(
        "models.User", related_name="cases"
    )

class Document(Model):
    id = fields.IntField(pk=True)
    # --- O>M for files
    status_processing_files = fields.CharField(max_length=20,null=True) # queued, processing, completed, error
    files = fields.ReverseRelation["File"]
    # --- content
    content = fields.ReverseRelation["DocumentContent"]
    # --- content -> embeddings
    status_processing_embeddings = fields.CharField(max_length=20,null=True) # queued, processing, completed, error
    embeddings = fields.ReverseRelation["Embedding"]
    # --- extracted summaries/details
    document_description = fields.TextField(null=True)
    document_summary = fields.TextField(null=True)

class DocumentContent(Model):
    id = fields.IntField(pk=True)
    # --- relations
    document: fields.ForeignKeyRelation[Document] = fields.ForeignKeyField(
        "models.Document", related_name="content", null=True
    )
    embedding = fields.ReverseRelation["Embedding"]
    # --- pdfs
    text = fields.TextField(null=True)
    tokenizing_strategy = fields.TextField(null=True)
    page_number = fields.CharField(max_length=255,null=True)
    # --- audio
    # TODO: time_start
    # TODO: time_end
    # --- pdfs + video?
    # TODO: image (file reltaion?)

class Embedding(Model):
    # Embeddings can come from source documents, but also from user queries. Seems like we should save those too as encoded type?
    id = fields.IntField(pk=True)
    # --- relations
    document: fields.ForeignKeyRelation[Document] = fields.ForeignKeyField(
        "models.Document", related_name="embeddings", null=True
    )
    document_content: fields.ForeignKeyRelation[DocumentContent] = fields.ForeignKeyField(
        "models.DocumentContent", related_name="embedding", null=True
    )
    # --- encoding model/engine info
    encoded_model = fields.TextField() # gpt3, clip
    encoded_model_engine = fields.TextField() # text-davinci-002 or text-similarity-davinci-001 vs. ViT-B/32 or ViT-L/14@336
    # --- pre-encoding
    encoding_strategy = fields.TextField() # image, text, page, minute, nsentence, sentence, ngram, user_request_question
    text = fields.TextField(null=True)
    # TODO: image?
    # --- post-encoding
    npy_url = fields.TextField(null=True) # save npy binary to S3 if we need to load later (seems better for storage than storing in the sql database as a byte-array)

class File(Model):
    id = fields.IntField(pk=True)
    # --- relations
    document: fields.ForeignKeyRelation[Document] = fields.ForeignKeyField(
        "models.Document", related_name="files", null=True
    )
    # ex: a 38 page PDF gets associated w/ the base document
    # embedding_id = fields.OneToOneRelation(Document) # ex: each page of the PDF gets associated w/ an embedding 
    # --- file props
    filename = fields.TextField()
    mime_type = fields.TextField(null=True)
    upload_key = fields.TextField(null=True)
    upload_url = fields.TextField(null=True)
    upload_thumbnail_url = fields.TextField(null=True)
