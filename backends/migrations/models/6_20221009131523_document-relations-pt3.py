from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "document" ALTER COLUMN "status_processing_files" DROP DEFAULT;
        ALTER TABLE "document" ALTER COLUMN "status_processing_text" DROP DEFAULT;
        CREATE TABLE "embedding_document" (
    "document_id" INT NOT NULL REFERENCES "document" ("id") ON DELETE CASCADE,
    "embedding_id" INT NOT NULL REFERENCES "embedding" ("id") ON DELETE CASCADE
);
        CREATE TABLE "file_document" (
    "file_id" INT NOT NULL REFERENCES "file" ("id") ON DELETE CASCADE,
    "document_id" INT NOT NULL REFERENCES "document" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "embedding_document";
        DROP TABLE IF EXISTS "file_document";
        ALTER TABLE "document" ALTER COLUMN "status_processing_files" SET DEFAULT 'queued';
        ALTER TABLE "document" ALTER COLUMN "status_processing_text" SET DEFAULT 'queued';"""
