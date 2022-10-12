from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "embedding_document";
        DROP TABLE IF EXISTS "file_document";
        ALTER TABLE "embedding" ADD "document_id" INT;
        ALTER TABLE "file" ADD "document_id" INT;
        ALTER TABLE "embedding" ADD CONSTRAINT "fk_embeddin_document_d22fd251" FOREIGN KEY ("document_id") REFERENCES "document" ("id") ON DELETE CASCADE;
        ALTER TABLE "file" ADD CONSTRAINT "fk_file_document_220d0576" FOREIGN KEY ("document_id") REFERENCES "document" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "embedding" DROP CONSTRAINT "fk_embeddin_document_d22fd251";
        ALTER TABLE "file" DROP CONSTRAINT "fk_file_document_220d0576";
        ALTER TABLE "file" DROP COLUMN "document_id";
        ALTER TABLE "embedding" DROP COLUMN "document_id";
        CREATE TABLE "file_document" (
    "file_id" INT NOT NULL REFERENCES "file" ("id") ON DELETE CASCADE,
    "document_id" INT NOT NULL REFERENCES "document" ("id") ON DELETE CASCADE
);
        CREATE TABLE "embedding_document" (
    "document_id" INT NOT NULL REFERENCES "document" ("id") ON DELETE CASCADE,
    "embedding_id" INT NOT NULL REFERENCES "embedding" ("id") ON DELETE CASCADE
);"""
