from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS `appset` (
    `id` CHAR(36) NOT NULL  PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `description` LONGTEXT NOT NULL,
    `privacy` VARCHAR(20) NOT NULL,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `model_name` VARCHAR(255) NOT NULL  DEFAULT 'gpt-3.5-turbo',
    `model_temperature` DOUBLE NOT NULL  DEFAULT 0.7,
    `model_max_tokens` INT NOT NULL  DEFAULT 4096,
    `model_history_window_length` INT NOT NULL  DEFAULT 4,
    `prompt_template` LONGTEXT NOT NULL,
    `citation_limit` INT NOT NULL  DEFAULT 4,
    `min_relevance` DOUBLE NOT NULL  DEFAULT 0.5
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `adminuser` (
    `id` CHAR(36) NOT NULL  PRIMARY KEY,
    `username` VARCHAR(255) NOT NULL UNIQUE,
    `hashed_password` VARCHAR(255) NOT NULL,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `chatset` (
    `id` CHAR(36) NOT NULL  PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL  DEFAULT 'new chat',
    `is_test` BOOL NOT NULL  DEFAULT 0,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `app_id_id` CHAR(36) NOT NULL,
    CONSTRAINT `fk_chatset_appset_bbcbb586` FOREIGN KEY (`app_id_id`) REFERENCES `appset` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `chathistory` (
    `id` CHAR(36) NOT NULL  PRIMARY KEY,
    `question` LONGTEXT NOT NULL,
    `answer` LONGTEXT NOT NULL,
    `cite_documents` JSON NOT NULL,
    `context_histories` JSON NOT NULL,
    `execute_time` DOUBLE NOT NULL,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `chat_id_id` CHAR(36) NOT NULL,
    CONSTRAINT `fk_chathist_chatset_407a6b40` FOREIGN KEY (`chat_id_id`) REFERENCES `chatset` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `dataset` (
    `id` CHAR(36) NOT NULL  PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `description` LONGTEXT NOT NULL,
    `privacy` VARCHAR(20) NOT NULL,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `article` (
    `id` CHAR(36) NOT NULL  PRIMARY KEY,
    `name` VARCHAR(255) NOT NULL,
    `character_count` INT NOT NULL  DEFAULT 0,
    `chunk_sum_num` INT NOT NULL  DEFAULT 0,
    `recall_count` INT NOT NULL  DEFAULT 0,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `updated_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    `dataset_id_id` CHAR(36) NOT NULL,
    CONSTRAINT `fk_article_dataset_73afc631` FOREIGN KEY (`dataset_id_id`) REFERENCES `dataset` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `fileset` (
    `id` CHAR(36) NOT NULL  PRIMARY KEY,
    `create_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `appset_id_id` CHAR(36) NOT NULL,
    `chat_id_id` CHAR(36)  UNIQUE,
    CONSTRAINT `fk_fileset_appset_17495ff5` FOREIGN KEY (`appset_id_id`) REFERENCES `appset` (`id`) ON DELETE CASCADE,
    CONSTRAINT `fk_fileset_chatset_3691d5c7` FOREIGN KEY (`chat_id_id`) REFERENCES `chatset` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `file` (
    `id` CHAR(36) NOT NULL  PRIMARY KEY,
    `filename` VARCHAR(255) NOT NULL,
    `create_time` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `fileset_id_id` CHAR(36) NOT NULL,
    CONSTRAINT `fk_file_fileset_d30a7743` FOREIGN KEY (`fileset_id_id`) REFERENCES `fileset` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `querytesthistory` (
    `id` CHAR(36) NOT NULL  PRIMARY KEY,
    `query` LONGTEXT NOT NULL,
    `k` INT NOT NULL,
    `min_relevance` DOUBLE NOT NULL,
    `created_at` DATETIME(6) NOT NULL  DEFAULT CURRENT_TIMESTAMP(6),
    `dataset_id_id` CHAR(36) NOT NULL,
    CONSTRAINT `fk_querytes_dataset_24256af0` FOREIGN KEY (`dataset_id_id`) REFERENCES `dataset` (`id`) ON DELETE CASCADE
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `aerich` (
    `id` INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
    `version` VARCHAR(255) NOT NULL,
    `app` VARCHAR(100) NOT NULL,
    `content` JSON NOT NULL
) CHARACTER SET utf8mb4;
CREATE TABLE IF NOT EXISTS `appset_dataset` (
    `appset_id` CHAR(36) NOT NULL,
    `dataset_id` CHAR(36) NOT NULL,
    FOREIGN KEY (`appset_id`) REFERENCES `appset` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`dataset_id`) REFERENCES `dataset` (`id`) ON DELETE CASCADE,
    UNIQUE KEY `uidx_appset_data_appset__07d766` (`appset_id`, `dataset_id`)
) CHARACTER SET utf8mb4;"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
