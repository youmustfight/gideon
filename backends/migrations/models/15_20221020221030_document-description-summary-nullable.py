from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "document" ADD "document_description" TEXT;
        ALTER TABLE "document" ADD "document_summary" TEXT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "document" DROP COLUMN "document_description";
        ALTER TABLE "document" DROP COLUMN "document_summary";"""
