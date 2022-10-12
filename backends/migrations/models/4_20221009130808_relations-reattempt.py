from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "document" ADD "status_processing_files" TEXT NOT NULL;
        ALTER TABLE "document" RENAME COLUMN "status_convert_to_text" TO "status_processing_text";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "document" RENAME COLUMN "status_processing_text" TO "status_convert_to_text";
        ALTER TABLE "document" DROP COLUMN "status_processing_files";"""
