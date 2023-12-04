from pathlib import Path
from os import mkdir
from os.path import exists, join

BASE_DIR = Path(__file__).resolve()

base_path = BASE_DIR.parent.parent.parent

database_path = join(base_path, "database")

save_base_image_path = join(database_path, "base_raffles_image")

tmp_path = join(base_path, "tmp")

# create dirs

paths = (base_path, database_path, save_base_image_path, tmp_path)
for path in paths:
    if not exists(path):
        mkdir(path)
