from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "case" ADD "organization_id" INT;
        ALTER TABLE "case" ADD CONSTRAINT "fk_case_organiza_4fd98653" FOREIGN KEY ("organization_id") REFERENCES "organization" ("id") ON DELETE CASCADE;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE "case" DROP CONSTRAINT "fk_case_organiza_4fd98653";
        ALTER TABLE "case" DROP COLUMN "organization_id";"""
