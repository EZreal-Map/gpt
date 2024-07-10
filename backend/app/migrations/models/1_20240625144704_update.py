from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `appset` (
    `id` CHAR(36) NOT NULL  PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `description` LONGTEXT NOT NULL,
    `privacy` VARCHAR(20) NOT NULL,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4;
        CREATE TABLE `appset_dataset` (
    `dataset_id` CHAR(36) NOT NULL REFERENCES `dataset` (`id`) ON DELETE CASCADE,
    `appset_id` CHAR(36) NOT NULL REFERENCES `appset` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS `appset_dataset`;
        DROP TABLE IF EXISTS `appset`;"""
