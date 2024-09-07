# import os
import subprocess

# DB_ENDPOINT="http://dynamo-test:8000"

# sub_env = os.environ.copy()
# sub_env["DB_ENDPOINT"] = DB_ENDPOINT
subprocess.run(args=["python", "create_table.py"])
