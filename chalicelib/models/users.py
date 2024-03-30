import os
import uuid
from datetime import datetime
from pynamodb.models import Model
from pynamodb.attributes import UTCDateTimeAttribute, UnicodeAttribute
from .microposts import Microposts


class Users(Model):
    class Meta:
        table_name = "Users"
        region = "ap-northeast-1"
        host = os.getenv("DB_ENDPOINT")
        write_capacity_units = 1
        read_capacity_units = 1

    issuer = UnicodeAttribute(hash_key=True)
    subject = UnicodeAttribute(range_key=True)
    id = UnicodeAttribute(null=False, default=str(uuid.uuid4()))
    createdAt = UTCDateTimeAttribute(null=False, default=datetime.now())
    updatedAt = UTCDateTimeAttribute(null=False, default=datetime.now())

    def post(self, content: str):
        return Microposts(userId=self.id, postedAt=datetime.now(), content=content)
