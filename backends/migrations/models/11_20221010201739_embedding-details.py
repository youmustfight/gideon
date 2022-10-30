from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "embedding" ADD "text" TEXT;
        ALTER TABLE "embedding" RENAME COLUMN "encoded_type" TO "encoding_strategy";
        ALTER TABLE "embedding" ADD "document_content_id" INT;
        ALTER TABLE "embedding" ADD "npy_url" TEXT;
        ALTER TABLE "embedding" ADD CONSTRAINT "fk_embeddin_document_f901d4e1" FOREIGN KEY ("document_content_id") REFERENCES "documentcontent" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "embedding" DROP CONSTRAINT "fk_embeddin_document_f901d4e1";
        ALTER TABLE "embedding" RENAME COLUMN "encoding_strategy" TO "encoded_type";
        ALTER TABLE "embedding" DROP COLUMN "text";
        ALTER TABLE "embedding" DROP COLUMN "document_content_id";
        ALTER TABLE "embedding" DROP COLUMN "npy_url";"""
