from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `chatset` ADD `name` VARCHAR(255) NOT NULL  DEFAULT '';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `chatset` DROP COLUMN `name`;"""
