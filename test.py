from app.setting import settings
import uuid
import os

file_dir = settings.current_dir
print(file_dir)
temp_dir = str(uuid.uuid4())
temp_path = file_dir.joinpath(temp_dir)
file_path = os.path.join(temp_path, "name.txt")
print(file_path)
