from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `adminuser` RENAME COLUMN `password` TO `hashed_password`;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `adminuser` RENAME COLUMN `hashed_password` TO `password`;"""
