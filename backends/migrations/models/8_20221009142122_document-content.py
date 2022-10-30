from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "document" RENAME COLUMN "status_processing_text" TO "status_processing_embeddings";
        ALTER TABLE "document" DROP COLUMN "document_text";
        ALTER TABLE "document" DROP COLUMN "document_text_by_page";
        CREATE TABLE IF NOT EXISTS "documentcontent" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "text" TEXT,
    "page_number" VARCHAR(255) NOT NULL,
    "documentdocument_id" INT REFERENCES "document" ("id") ON DELETE CASCADE
);;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "document" ADD "document_text" TEXT;
        ALTER TABLE "document" RENAME COLUMN "status_processing_embeddings" TO "status_processing_text";
        ALTER TABLE "document" ADD "document_text_by_page" text[];
        DROP TABLE IF EXISTS "documentcontent";"""
