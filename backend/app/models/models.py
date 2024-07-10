from tortoise.models import Model
from tortoise import fields

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
    