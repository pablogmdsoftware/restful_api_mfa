import os
from time import sleep
from sqlmodel import SQLModel
from models import create_db_and_tables
from utils import BASE_DIR

if __name__ == "__main__":
    folder_path = os.path.join(BASE_DIR, "database")
    os.makedirs(folder_path, exist_ok=True)
    while not os.path.exists(folder_path):
        sleep(0.1)
    create_db_and_tables()