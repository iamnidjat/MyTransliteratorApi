from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    REDIS_HOST: str
    REDIS_PORT: int
    REDIS_PASSWORD: str

    # Pydantic v2
    model_config = {
        "env_file": ".env",  # tells Pydantic to also look in the .env file for values of these settings
        "extra": "allow"  # allows any other keys in the .env without error
    }

settings = Settings()