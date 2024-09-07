import os
from chalicelib.models import Users, Microposts


print(os.environ)


if __name__ == "__main__":
    if not Users.exists():
        Users.create_table()

    if not Microposts.exists():
        Microposts.create_table()
