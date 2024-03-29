from chalicelib.models import Users, Microposts

if __name__ == "__main__":
    if not Users.exists():
        Users.create_table()

    if not Microposts.exists():
        Microposts.create_table()
