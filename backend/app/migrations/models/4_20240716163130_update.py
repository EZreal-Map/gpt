from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `appset` MODIFY COLUMN `prompt_template` LONGTEXT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `appset` MODIFY COLUMN `prompt_template` LONGTEXT NOT NULL;"""
