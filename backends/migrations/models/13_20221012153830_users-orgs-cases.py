from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "case" (
    "id" SERIAL NOT NULL PRIMARY KEY
);;
        CREATE TABLE "organization_user" (
    "organization_id" INT NOT NULL REFERENCES "organization" ("id") ON DELETE CASCADE,
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE
);
        CREATE TABLE "case_user" (
    "user_id" INT NOT NULL REFERENCES "user" ("id") ON DELETE CASCADE,
    "case_id" INT NOT NULL REFERENCES "case" ("id") ON DELETE CASCADE
);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "organization_user";
        DROP TABLE IF EXISTS "case";"""
