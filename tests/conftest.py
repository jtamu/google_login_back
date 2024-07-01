import pytest
import subprocess
import time
import os


@pytest.fixture(scope="session")
def start_chalice_local():
    process = subprocess.Popen(
        ["chalice", "local", "--host=0.0.0.0", f"--port={os.getenv('TEST_PORT')}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    # サービスが完全に起動するまで待機
    time.sleep(5)
    yield
    process.terminate()
    process.wait()
