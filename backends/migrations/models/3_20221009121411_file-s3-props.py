from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "document" ADD "status_convert_to_text" TEXT NOT NULL;
        ALTER TABLE "document" ADD "document_text_by_page" text[] NOT NULL;
        ALTER TABLE "document" DROP COLUMN "file_thumbnail_url";
        ALTER TABLE "document" DROP COLUMN "file_url";
        ALTER TABLE "document" DROP COLUMN "filename";
        ALTER TABLE "document" DROP COLUMN "mime_type";
        ALTER TABLE "embedding" ADD "encoded_model" TEXT NOT NULL;
        ALTER TABLE "embedding" ADD "encoded_model_engine" TEXT NOT NULL;
        ALTER TABLE "embedding" ADD "encoded_type" TEXT NOT NULL;
        CREATE TABLE IF NOT EXISTS "file" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "filename" TEXT NOT NULL,
    "mime_type" TEXT NOT NULL,
    "upload_key" TEXT NOT NULL,
    "upload_url" TEXT NOT NULL,
    "upload_thumbnail_url" TEXT NOT NULL
);;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "document" ADD "file_thumbnail_url" TEXT NOT NULL;
        ALTER TABLE "document" ADD "file_url" TEXT NOT NULL;
        ALTER TABLE "document" ADD "filename" TEXT NOT NULL;
        ALTER TABLE "document" ADD "mime_type" TEXT NOT NULL;
        ALTER TABLE "document" DROP COLUMN "status_convert_to_text";
        ALTER TABLE "document" DROP COLUMN "document_text_by_page";
        ALTER TABLE "embedding" DROP COLUMN "encoded_model";
        ALTER TABLE "embedding" DROP COLUMN "encoded_model_engine";
        ALTER TABLE "embedding" DROP COLUMN "encoded_type";
        DROP TABLE IF EXISTS "file";"""
