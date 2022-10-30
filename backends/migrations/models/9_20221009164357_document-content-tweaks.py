from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "documentcontent" ALTER COLUMN "page_number" DROP NOT NULL;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "documentcontent" ALTER COLUMN "page_number" SET NOT NULL;"""
