from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "document" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "filename" TEXT NOT NULL,
    "file_url" TEXT NOT NULL,
    "file_thumbnail_url" TEXT NOT NULL,
    "mime_type" TEXT NOT NULL,
    "document_text" TEXT NOT NULL
);;
        CREATE TABLE IF NOT EXISTS "embedding" (
    "id" SERIAL NOT NULL PRIMARY KEY
);;
        CREATE TABLE IF NOT EXISTS "user" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "name" TEXT NOT NULL
);;
        DROP TABLE IF EXISTS "users";
        DROP TABLE IF EXISTS "documents";"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "document";
        DROP TABLE IF EXISTS "embedding";
        DROP TABLE IF EXISTS "user";"""
