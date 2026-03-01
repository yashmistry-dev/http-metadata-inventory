from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    mongodb_url: str = "mongodb://admin:password@localhost:27018/"
    mongodb_db_name: str = "metadata_db"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    http_timeout: int = 30
    http_max_redirects: int = 5
    http_verify_ssl: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

