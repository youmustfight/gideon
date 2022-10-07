from tortoise import Model, fields

class Documents(Model):
    id = fields.IntField(pk=True)
    filename = fields.TextField()
    mime_type = fields.TextField()


class Users(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()

