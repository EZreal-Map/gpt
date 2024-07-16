from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `appset` ADD `min_relevance` DOUBLE NOT NULL  DEFAULT 0.5;
        ALTER TABLE `appset` ADD `model_max_tokens` INT NOT NULL;
        ALTER TABLE `appset` ADD `model_temperature` DOUBLE NOT NULL  DEFAULT 0.7;
        ALTER TABLE `appset` ADD `model_name` VARCHAR(255) NOT NULL  DEFAULT 'gpt-3.5-turbo';
        ALTER TABLE `appset` ADD `prompt_template` LONGTEXT NOT NULL;
        ALTER TABLE `appset` ADD `model_history_window_length` INT NOT NULL  DEFAULT 10;
        ALTER TABLE `appset` ADD `citation_limit` INT NOT NULL  DEFAULT 4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        ALTER TABLE `appset` DROP COLUMN `min_relevance`;
        ALTER TABLE `appset` DROP COLUMN `model_max_tokens`;
        ALTER TABLE `appset` DROP COLUMN `model_temperature`;
        ALTER TABLE `appset` DROP COLUMN `model_name`;
        ALTER TABLE `appset` DROP COLUMN `prompt_template`;
        ALTER TABLE `appset` DROP COLUMN `model_history_window_length`;
        ALTER TABLE `appset` DROP COLUMN `citation_limit`;"""
