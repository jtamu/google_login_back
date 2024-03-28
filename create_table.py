from chalicelib.models import Users

if __name__ == "__main__":
    if not Users.exists():
        Users.create_table()
