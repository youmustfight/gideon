
import sqlalchemy as sa
from dbs.sa_models import Document, File
from files.s3_utils import s3_get_file_url, s3_upload_file

async def index_document_prep(session, pyfile, case_id, type):
    # VALIDATE
    print(f"INFO (index_document_prep.py): type: '{type}'")
    if type not in ['audio', 'docx', 'image', 'pdf', 'video']:
        raise f'Document type not allowed: {type}'
    # SAVE DOCUMENT
    document_query = await session.execute(
        sa.insert(Document)
            .values(name=pyfile.name, status_processing_files="queued", type=type, case_id=case_id)
            .returning(Document.id)) # can't seem to return anything except id
    document_id = document_query.scalar_one_or_none()
    # SAVE FILE TO S3
    print(f"INFO (index_document_prep.py): index_document id {document_id}")
    filename = pyfile.name
    upload_key = pyfile.name # TODO: avoid collisions w/ unique prefix
    # --- save to S3
    s3_upload_file(upload_key, pyfile)
    # RELATE FILE BACK TO DOCUMENT
    session.add(File(
        filename=pyfile.name,
        mime_type=pyfile.type,
        upload_key=upload_key,
        upload_url=s3_get_file_url(filename),
        document_id=document_id
    ))
    # UPDATE PROCESSING STATUS (kind of silly bc of above queued and an err will rollback either)
    await session.execute(sa.update(Document)
        .where(Document.id == int(document_id))
        .values(status_processing_files="completed"))
    # RETURN DOCUMENT
    return document_id
