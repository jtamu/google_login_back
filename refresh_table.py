from chalicelib.models import Users, Microposts


if __name__ == "__main__":
    Users.delete_table()
    Users.create_table()
    Microposts.delete_table()
    Microposts.create_table()
