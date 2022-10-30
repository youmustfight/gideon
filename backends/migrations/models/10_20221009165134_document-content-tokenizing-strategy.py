from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "documentcontent" ADD "tokenizing_strategy" TEXT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "documentcontent" DROP COLUMN "tokenizing_strategy";"""
