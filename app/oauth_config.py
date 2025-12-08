"""
Zoho Directory OAuth2 Configuration
"""
import os
from authlib.integrations.starlette_client import OAuth
from dotenv import load_dotenv

load_dotenv()

# Zoho OAuth2 Configuration
ZOHO_CLIENT_ID = os.getenv("ZOHO_CLIENT_ID", "")
ZOHO_CLIENT_SECRET = os.getenv("ZOHO_CLIENT_SECRET", "")
ZOHO_REDIRECT_URI = os.getenv("ZOHO_REDIRECT_URI", "http://localhost:8001/api/v1/auth/callback")
ZOHO_DOMAIN = os.getenv("ZOHO_DOMAIN", "accounts.zoho.in")  # Can be accounts.zoho.eu, accounts.zoho.in, etc.
ZOHO_USERINFO_URL = f"https://{ZOHO_DOMAIN}/oauth/user/info"

# JWT Configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))


# Initialize OAuth
oauth = OAuth()


# Register Zoho OAuth2 provider
oauth.register(
    name='zoho',
    client_id=ZOHO_CLIENT_ID,
    client_secret=ZOHO_CLIENT_SECRET,
    server_metadata_url=f'https://{ZOHO_DOMAIN}/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid profile email ZohoDirectory.users.READ'
    }
)
