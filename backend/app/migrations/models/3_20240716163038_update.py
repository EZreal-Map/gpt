from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `appset` MODIFY COLUMN `model_max_tokens` INT;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `appset` MODIFY COLUMN `model_max_tokens` INT NOT NULL;"""
