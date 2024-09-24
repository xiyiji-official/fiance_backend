from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List


class Settings(BaseSettings):
    db_url: str
    template_path: str
    config_path: str
    # 获取当前文件的目录
    admin_secret_key: str
    allowed_origins: str
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = Path(__file__).resolve().parent.joinpath(".env")

    @property
    def current_dir(self) -> Path:
        return Path(__file__).resolve().parent.parent

    @property
    def origins(self) -> List[str]:
        return self.allowed_origins.split(",")

    @property
    def template(self) -> List[str]:
        return self.current_dir.joinpath(self.template_path)

    @property
    def config(self) -> List[str]:
        return self.current_dir.joinpath(self.config_path)


settings = Settings()
