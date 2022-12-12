import sqlalchemy as sa
from sqlalchemy.orm import joinedload

from agents.ai_action_agent import create_ai_action_agent, AI_ACTIONS
from dbs.sa_models import Document, DocumentContent, Embedding, File
from files.s3_utils import s3_get_file_url
from models.clip import clip_classifications

async def _index_document_image_process_content(session, document_id) -> None:
    document_query = await session.execute(sa.select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    # 1. STATUS
    files_query = await session.execute(sa.select(File).where(File.document_id == document_id))
    files = files_query.scalars()
    print(f"INFO (index_document_image.py:_index_document_image_process_content) ##TODO## files")
    file = files.first()
    # 2. DOCUMENT CONTENT CREATE
    document_content = DocumentContent(
        document_id=document_id,
        image_file_id=file.id
    )
    session.add(document_content)
    # 3. SAVE
    document.status_processing_content = "completed"
    session.add(document)

async def _index_document_image_process_embeddings(session, document_id) -> None:
    print('INFO (index_document_image.py:_index_document_image_process_embeddings): start')
    # SETUP
    document_query = await session.execute(sa.select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    document_content_query = await session.execute(sa.select(DocumentContent).where(DocumentContent.document_id == document_id))
    document_content = document_content_query.scalars().all()
    print('INFO (index_document_image.py:_index_document_image_process_embeddings): document content', document_content)
    # CREATE EMBEDDINGS (context is derived from relation)
    # --- agent
    aiagent_image_embeder = await create_ai_action_agent(session, action=AI_ACTIONS.document_similarity_image_embed, case_id=document.case_id)
    # --- images
    image_embeddings_as_models = []
    for content in list(document_content):
        document_content_file_query = await session.execute(
            sa.select(File)
                .options(joinedload(File.document_content_image_file))
                .where(File.document_content_image_file.any(DocumentContent.id == int(content.id))))
        document_content_file = document_content_file_query.scalars().first()
        # --- run through clip
        image_embeddings = aiagent_image_embeder.encode_image([s3_get_file_url(document_content_file.upload_key)])
        image_embeddings_as_models.append(Embedding(
            document_id=document_id,
            document_content_id=content.id,
            encoded_model_engine=aiagent_image_embeder.model_name,
            encoding_strategy="image",
            vector_json=image_embeddings[0].tolist(),
        ))
    session.add_all(image_embeddings_as_models)
    # --- SAVE
    document.status_processing_embeddings = "completed"
    session.add(document)

async def _index_document_image_process_extractions(session, document_id) -> None:
    print('INFO (index_document_image.py:_index_document_image_process_extractions): start')
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
    print('INFO (index_document_image.py): document_description', document.document_description)
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
    print('INFO (index_document_image.py): document_summary', document.document_summary)
    # 4. SAVE
    document.status_processing_extractions = "completed"
    session.add(document)


async def index_document_image(session, document_id) -> int:
    print(f"INFO (index_document_image.py): indexing document #{document_id}")
    try:
        # PROCESS FILE & EMBEDDINGS
        print(f"INFO (index_document_image.py): processing document #{document_id} content")
        await _index_document_image_process_content(session=session, document_id=document_id)
        print(f"INFO (index_document_image.py): processing document #{document_id} embeddings")
        await _index_document_image_process_embeddings(session=session, document_id=document_id)
        print(f"INFO (index_document_image.py): processing document #{document_id} extractions")
        await _index_document_image_process_extractions(session=session, document_id=document_id)
        print(f"INFO (index_document_image.py): finished intake of document #{document_id}")
        # RETURN (SAVE/COMMIT happens via context/caller of this func)
        return document_id
    except Exception as err:
        print(f"ERROR (index_document_image.py):", err)
        raise err # by throwing the error up to the route context(with), we'll trigger a rollback automatically
