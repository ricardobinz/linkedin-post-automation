from __future__ import annotations
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

# Load environment from .env if present
load_dotenv()


def getenv(name: str, default: str = "") -> str:
    return os.getenv(name, default)


@dataclass
class LinkedInConfig:
    client_id: str = getenv("LINKEDIN_CLIENT_ID")
    client_secret: str = getenv("LINKEDIN_CLIENT_SECRET")
    redirect_uri: str = getenv("LINKEDIN_REDIRECT_URI")
    access_token: str = getenv("LINKEDIN_ACCESS_TOKEN")
    author_urn: str = getenv("LINKEDIN_AUTHOR_URN")
    organization_urn: str = getenv("LINKEDIN_ORGANIZATION_URN")


@dataclass
class Settings:
    port: int = int(getenv("PORT", "4000"))
    api_key: str = getenv("API_KEY")
    anthropic_api_key: str = getenv("ANTHROPIC_API_KEY")
    perplexity_api_key: str = getenv("PERPLEXITY_API_KEY")
    openai_api_key: str = getenv("OPENAI_API_KEY")
    linkedin: LinkedInConfig = field(default_factory=LinkedInConfig)


settings = Settings()
