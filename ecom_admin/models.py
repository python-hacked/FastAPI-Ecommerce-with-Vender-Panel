from tortoise.models import Model
from tortoise import Tortoise, fields
from fastapi import FastAPI
from tortoise import Tortoise


class Register_admin(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(50,)
    email = fields.CharField(50, unique=True)
    phone = fields.CharField(10)
    password = fields.CharField(200)
    address = fields.CharField(100)
    admin_image = fields.TextField()


    Tortoise.init_models(['ecom_API.models'], 'models')