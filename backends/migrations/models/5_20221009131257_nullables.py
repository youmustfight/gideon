from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "document" ALTER COLUMN "document_text_by_page" DROP NOT NULL;
        ALTER TABLE "document" ALTER COLUMN "document_text" DROP NOT NULL;
        ALTER TABLE "document" ALTER COLUMN "status_processing_text" SET DEFAULT 'queued';
        ALTER TABLE "document" ALTER COLUMN "status_processing_text" DROP NOT NULL;
        ALTER TABLE "document" ALTER COLUMN "status_processing_text" TYPE VARCHAR(20) USING "status_processing_text"::VARCHAR(20);
        ALTER TABLE "document" ALTER COLUMN "status_processing_text" TYPE VARCHAR(20) USING "status_processing_text"::VARCHAR(20);
        ALTER TABLE "document" ALTER COLUMN "status_processing_text" TYPE VARCHAR(20) USING "status_processing_text"::VARCHAR(20);
        ALTER TABLE "document" ALTER COLUMN "status_processing_files" SET DEFAULT 'queued';
        ALTER TABLE "document" ALTER COLUMN "status_processing_files" DROP NOT NULL;
        ALTER TABLE "document" ALTER COLUMN "status_processing_files" TYPE VARCHAR(20) USING "status_processing_files"::VARCHAR(20);
        ALTER TABLE "document" ALTER COLUMN "status_processing_files" TYPE VARCHAR(20) USING "status_processing_files"::VARCHAR(20);
        ALTER TABLE "document" ALTER COLUMN "status_processing_files" TYPE VARCHAR(20) USING "status_processing_files"::VARCHAR(20);
        ALTER TABLE "file" ALTER COLUMN "upload_url" DROP NOT NULL;
        ALTER TABLE "file" ALTER COLUMN "upload_key" DROP NOT NULL;
        ALTER TABLE "file" ALTER COLUMN "upload_thumbnail_url" DROP NOT NULL;
        ALTER TABLE "file" ALTER COLUMN "mime_type" DROP NOT NULL;
        ALTER TABLE "user" ALTER COLUMN "name" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "file" ALTER COLUMN "upload_url" SET NOT NULL;
        ALTER TABLE "file" ALTER COLUMN "upload_key" SET NOT NULL;
        ALTER TABLE "file" ALTER COLUMN "upload_thumbnail_url" SET NOT NULL;
        ALTER TABLE "file" ALTER COLUMN "mime_type" SET NOT NULL;
        ALTER TABLE "user" ALTER COLUMN "name" SET NOT NULL;
        ALTER TABLE "document" ALTER COLUMN "document_text_by_page" SET NOT NULL;
        ALTER TABLE "document" ALTER COLUMN "document_text" SET NOT NULL;
        ALTER TABLE "document" ALTER COLUMN "status_processing_text" TYPE TEXT USING "status_processing_text"::TEXT;
        ALTER TABLE "document" ALTER COLUMN "status_processing_text" SET NOT NULL;
        ALTER TABLE "document" ALTER COLUMN "status_processing_text" DROP DEFAULT;
        ALTER TABLE "document" ALTER COLUMN "status_processing_text" TYPE TEXT USING "status_processing_text"::TEXT;
        ALTER TABLE "document" ALTER COLUMN "status_processing_text" TYPE TEXT USING "status_processing_text"::TEXT;
        ALTER TABLE "document" ALTER COLUMN "status_processing_files" TYPE TEXT USING "status_processing_files"::TEXT;
        ALTER TABLE "document" ALTER COLUMN "status_processing_files" SET NOT NULL;
        ALTER TABLE "document" ALTER COLUMN "status_processing_files" DROP DEFAULT;
        ALTER TABLE "document" ALTER COLUMN "status_processing_files" TYPE TEXT USING "status_processing_files"::TEXT;
        ALTER TABLE "document" ALTER COLUMN "status_processing_files" TYPE TEXT USING "status_processing_files"::TEXT;"""
