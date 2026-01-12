import os

def pytest_configure():
    os.environ["TESTING"] = "1"