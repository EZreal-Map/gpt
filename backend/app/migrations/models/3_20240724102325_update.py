from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `adminuser` ADD UNIQUE INDEX `uid_adminuser_usernam_e7e1a7` (`username`);"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `adminuser` DROP INDEX `idx_adminuser_usernam_e7e1a7`;"""
