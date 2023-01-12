import sqlalchemy as sa
from dbs.sa_models import Document, DocumentContent, Embedding, File
from indexers.utils.extract_document_events import extract_document_events_v1
from indexers.utils.extract_document_summary import extract_document_summary
from indexers.utils.extract_document_summary_one_liner import extract_document_summary_one_liner
from indexers.utils.tokenize_string import TOKENIZING_STRATEGY

async def process_document_extras(session, document_id: int) -> None:
    print('INFO (process_document_extras.py): start')
    # FETCH
    document_query = await session.execute(sa.select(Document).where(Document.id == document_id))
    document = document_query.scalars().one()
    document_content_query = await session.execute(sa.select(DocumentContent).where(DocumentContent.document_id == document_id))
    document_content = document_content_query.scalars()
    document_content_text = " ".join(map(
        lambda content: content.text if content.tokenizing_strategy == TOKENIZING_STRATEGY.sentence.value else "", document_content))

    # COMPILE/EXTRACT
    # --- classification/description (DOING THIS ON INITIAL INDEXING FOR SOME IMMEDIATE FLAVOR TEXT AND CAUSE ITS FAST-ISH)
    # --- summary
    print(f'INFO (process_document_extras.py): document_summary. len = {len(document_content_text)}')
    if len(document_content_text) > 0 and len(document_content_text) < 250_000:
        document.generated_summary = extract_document_summary(document_content_text)
        document.generated_summary_one_liner = extract_document_summary_one_liner(document.generated_summary)
    # --- TODO: event timeline v2
    # --- TODO: cases/laws mentioned
    # --- TODO: organizations mentioned
    # --- TODO: people mentioned + context within document

    # SAVE
    document.status_processing_extractions = "completed"
    session.add(document)

