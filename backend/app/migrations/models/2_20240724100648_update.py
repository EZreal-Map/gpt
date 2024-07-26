from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `adminuser` (
    `id` CHAR(36) NOT NULL  PRIMARY KEY,
    `username` VARCHAR(255) NOT NULL,
    `password` VARCHAR(255) NOT NULL,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4;
        ALTER TABLE `chatset` ALTER COLUMN `name` SET DEFAULT 'new chat';"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `chatset` ALTER COLUMN `name` SET DEFAULT '';
        DROP TABLE IF EXISTS `adminuser`;"""
