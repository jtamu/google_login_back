import os
from datetime import datetime
from pynamodb.models import Model
from pynamodb.attributes import UTCDateTimeAttribute, UnicodeAttribute


class Microposts(Model):
    class Meta:
        table_name = "Microposts"
        region = "ap-northeast-1"
        host = os.getenv("DB_ENDPOINT")
        write_capacity_units = 1
        read_capacity_units = 1

    userId = UnicodeAttribute(hash_key=True, null=False)
    postedAt = UTCDateTimeAttribute(range_key=True, null=False)
    content = UnicodeAttribute(null=False)
    createdAt = UTCDateTimeAttribute(null=False, default=datetime.now())
    updatedAt = UTCDateTimeAttribute(null=False, default=datetime.now())
