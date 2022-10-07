from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "documents" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "filename" TEXT NOT NULL,
    "mime_type" TEXT NOT NULL
);;
        ALTER TABLE "users" ALTER COLUMN "name" TYPE TEXT USING "name"::TEXT;
        ALTER TABLE "users" ALTER COLUMN "name" TYPE TEXT USING "name"::TEXT;
        ALTER TABLE "users" ALTER COLUMN "name" TYPE TEXT USING "name"::TEXT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "users" ALTER COLUMN "name" TYPE VARCHAR(50) USING "name"::VARCHAR(50);
        ALTER TABLE "users" ALTER COLUMN "name" TYPE VARCHAR(50) USING "name"::VARCHAR(50);
        ALTER TABLE "users" ALTER COLUMN "name" TYPE VARCHAR(50) USING "name"::VARCHAR(50);
        DROP TABLE IF EXISTS "documents";"""
