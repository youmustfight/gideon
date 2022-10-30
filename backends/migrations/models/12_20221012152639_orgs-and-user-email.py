from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "organization" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" TEXT
);;
        ALTER TABLE "user" ADD "email" TEXT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "user" DROP COLUMN "email";
        DROP TABLE IF EXISTS "organization";"""
