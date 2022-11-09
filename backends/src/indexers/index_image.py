import json
import openai
from sentence_transformers import SentenceTransformer
import sqlalchemy as sa
import numpy as np
from sqlalchemy.orm import joinedload

from dbs.sa_models import Document, DocumentContent, Embedding, File
from dbs.vectordb_pinecone import index_clip_image_add
import env
from files.file_utils import get_file_path
from files.s3_utils import s3_get_file_bytes, s3_get_file_url, s3_upload_file
from models.clip import clip_classifications, clip_image_embedding, clip_vars

# SETUP
# --- OpenAI
openai.api_key = env.env_get_open_ai_api_key()

async def _index_image_process_content(session, document_id) -> None:
    document_query = await session.execute(sa.select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    # 1. STATUS
    files_query = await session.execute(sa.select(File).where(File.document_id == document_id))
    files = files_query.scalars()
    print(f"INFO (index_image.py:_index_image_process_content) ##TODO## files")
    file = files.first()
    # 2. DOCUMENT CONTENT CREATE
    document_content = DocumentContent(
        document_id=document_id,
        image_file_id=file.id
    )
    session.add(document_content)
    # 3. SAVE
    document.name = file.filename
    document.type = "image"
    document.status_processing_files = "completed"
    document.status_processing_content = "completed"
    session.add(document)

async def _index_image_process_embeddings(session, document_id) -> None:
    print('INFO (index_pdf.py:_index_image_process_embeddings): start')
    document_query = await session.execute(sa.select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    document_content_query = await session.execute(sa.select(DocumentContent).where(DocumentContent.document_id == document_id))
    document_content = document_content_query.scalars().all()
    print('INFO (index_pdf.py:_index_image_process_embeddings): document content', document_content)
    # --- CREATE EMBEDDINGS (context is derived from relation)
    for content in list(document_content):
        document_content_file_query = await session.execute(
            sa.select(File)
                .options(joinedload(File.document_content_image_file))
                .where(File.document_content_image_file.any(DocumentContent.id == int(content.id))))
        document_content_file = document_content_file_query.scalars().first()
        # --- run through clip
        image_embedding_tensor = clip_image_embedding(s3_get_file_url(document_content_file.upload_key)) # returns numpy array [1,512]
        print('INFO (index_pdf.py:_index_image_process_embeddings): document image_embedding_tensor.shape', image_embedding_tensor.shape)
        image_embedding_vector = np.squeeze(image_embedding_tensor).tolist()
        print('INFO (index_pdf.py:_index_image_process_embeddings): document image_embedding_vector', image_embedding_vector)
        # --- creat embedding
        await session.execute(
            sa.insert(Embedding).values(
                document_id=document_id,
                document_content_id=content.id,
                encoded_model="clip",
                encoded_model_engine=clip_vars()["CLIP_MODEL"],
                encoding_strategy="image",
                vector_json=image_embedding_vector,
            ))
    # --- SAVE
    document.status_processing_embeddings = "completed"
    session.add(document)

async def _index_image_process_extractions(session, document_id) -> None:
    print('INFO (index_pdf.py:_index_image_process_extractions): start')
    document_query = await session.execute(sa.select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    # 1. vectors... for search... inspired by... https://adeshg7.medium.com/build-your-own-search-engine-using-openais-clip-and-fastapi-part-1-89995aefbcdd
    files_query = await session.execute(sa.select(File).where(File.document_id == document_id))
    files = files_query.scalars()
    file = files.first()
    image_file_urls = [s3_get_file_url(file.upload_key)]
    # 2. document description (ex: mug shot, crime scene, etc. high level)
    document_type_classifications = []
    document_type_classifications +=  clip_classifications(
        classifications=["a mugshot photo", "a photo of a crime scene"],
        image_file_urls=image_file_urls,
        min_similarity=0.6
    )[0]
    document.document_description = ", ".join(map(lambda prediction: prediction['classification'], document_type_classifications))
    print('INFO (index_image.py): document_description', document.document_description)
    # 3. document summary (multiple breakdowns w/ contrast between classifications)
    document_summary_classifications = []
    document_summary_classifications += clip_classifications(
        classifications=["a photo during the day", "a photo during the night"],
        image_file_urls=image_file_urls,
        min_similarity=0.6
    )[0]
    document_summary_classifications += clip_classifications(
        classifications=["a photo of a person", "a photo containing multiple people", "a photo containing no people", "a photo containing documents"],
        image_file_urls=image_file_urls,
        min_similarity=0.6
    )[0]
    document_summary_classifications += clip_classifications(
        classifications=["a photo indoors", "a photo outdoors"],
        image_file_urls=image_file_urls,
        min_similarity=0.6
    )[0]
    document.document_summary = ", ".join(map(lambda prediction: prediction['classification'], document_summary_classifications))
    print('INFO (index_image.py): document_summary', document.document_summary)
    # 4. SAVE
    document.status_processing_extractions = "completed"
    session.add(document)


async def index_image(session, pyfile) -> int:
    print(f"INFO (index_image.py): indexing {pyfile.name} ({pyfile.type})")
    try:
        # SETUP DOCUMENT
        document_query = await session.execute(
            sa.insert(Document)
                .values(status_processing_files="queued")
                .returning(Document.id)) # can't seem to return anything except id
        document_id = document_query.scalar_one_or_none()
        print(f"INFO (index_image.py): index_document id {document_id}")
        # SAVE & RELATE FILE
        filename = pyfile.name
        upload_key = pyfile.name # TODO: avoid collisions w/ unique prefix
        # --- save to S3
        s3_upload_file(upload_key, pyfile)
        # --- create File()
        input_s3_url = s3_get_file_url(filename)
        session.add(File(
            filename=pyfile.name,
            mime_type=pyfile.type,
            upload_key=upload_key,
            upload_url=input_s3_url,
            document_id=document_id
        ))
        # PROCESS FILE & EMBEDDINGS
        print(f"INFO (index_image.py): processing file", upload_key)
        await _index_image_process_content(session=session, document_id=document_id)
        print(f"INFO (index_image.py): processing embeddings", upload_key)
        await _index_image_process_embeddings(session=session, document_id=document_id)
        print(f"INFO (index_image.py): processing extractions", upload_key)
        await _index_image_process_extractions(session=session, document_id=document_id)
        print(f"INFO (index_image.py): finished intake of document #{document_id}")
        # RETURN (SAVE/COMMIT happens via context/caller of this func)
        return document_id
    except Exception as err:
        print(f"ERROR (index_image.py):", err)
        raise err # by throwing the error up to the route context(with), we'll trigger a rollback automatically
