from tortoise.models import Model
from tortoise import fields
from utils.templates import retrieval_template

class DataSet(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField()
    privacy = fields.CharField(max_length=20)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

class Article(Model):
    id = fields.UUIDField(pk=True)
    dataset_id = fields.ForeignKeyField('models.DataSet', related_name='articles', on_delete=fields.CASCADE)
    name = fields.CharField(max_length=255)
    character_count = fields.IntField(default=0)
    chunk_sum_num = fields.IntField(default=0)
    recall_count = fields.IntField(default=0)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

class QueryTestHistory(Model):
    id = fields.UUIDField(pk=True)
    dataset_id = fields.ForeignKeyField('models.DataSet', related_name='query_test_histories', on_delete=fields.CASCADE)
    query = fields.TextField()
    k = fields.IntField()
    min_relevance = fields.FloatField()
    created_at = fields.DatetimeField(auto_now_add=True)

class APPSet(Model):
    id = fields.UUIDField(pk=True)
    name = fields.CharField(max_length=255)
    description = fields.TextField()
    privacy = fields.CharField(max_length=20)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)
    datasets = fields.ManyToManyField('models.DataSet', related_name='appsets')
    # 大语言模型有关参数字段
    model_name = fields.CharField(max_length=255, default="gpt-3.5-turbo")
    model_temperature = fields.FloatField(default=0.7)
    # 4096是openai所有模型的最大输出token长度，区别在于上下文长度context_length
    model_max_tokens = fields.IntField(default=4096) 
    model_history_window_length = fields.IntField(default=4)
    # 提示词模板字段
    prompt_template = fields.TextField(default=retrieval_template) # 使用默认模板
    # 关联知识库有关参数字段
    citation_limit = fields.IntField(default=4)
    min_relevance = fields.FloatField(default=0.5)

class ChatSet(Model):
    id = fields.UUIDField(pk=True)
    app_id = fields.ForeignKeyField('models.APPSet', related_name='chatsets', on_delete=fields.CASCADE)
    name = fields.CharField(max_length=255, default='new chat')
    is_test = fields.BooleanField(default=False)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

class ChatHistory(Model):
    id = fields.UUIDField(pk=True)
    chat_id = fields.ForeignKeyField('models.ChatSet', related_name='histories', on_delete=fields.CASCADE)
    question = fields.TextField()
    answer = fields.TextField()
    cite_documents = fields.JSONField()  # 用于存储检索到的引用记录
    context_histories = fields.JSONField()  # 用于存储历史上下文记录
    execute_time = fields.FloatField()
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)