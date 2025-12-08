from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from starlette.middleware.sessions import SessionMiddleware

from .database import engine, Base
from .api.v1 import auth, leases, schedules, payments
from .oauth_config import SECRET_KEY

import sys
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(
    title="Lease Accounting API",
    description="""
## Lease Accounting API with Zoho Directory OAuth2 Authentication

This API provides lease accounting schedule generation for ASC 842 (US GAAP) and IFRS 16 (International) standards.

### Authentication

All endpoints except `/auth/login` and `/auth/callback` require authentication using Bearer tokens issued after Zoho login.

**To get started:**
1. Visit `/api/v1/auth/login` to initiate Zoho OAuth2 login
2. After successful login, you'll receive a JWT access token
3. Click the **🔓 Authorize** button and enter your token
4. Or add `Bearer <token>` to the Authorization header manually

### OAuth2 Flow
1. User visits `/api/v1/auth/login`
2. Redirected to Zoho login page
3. After login, redirected back to `/api/v1/auth/callback`
4. Receive JWT token in response
5. Use token for all subsequent API calls
    """,
    version="1.0.0",
    swagger_ui_parameters={
        "persistAuthorization": True,
    }
)

# Custom OpenAPI schema to add security definitions
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Add security schemes
    openapi_schema["components"]["securitySchemes"] = {
        "Bearer": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": "Enter the Bearer token returned after Zoho login"
        }
    }

    # Apply security to all endpoints except auth login and callback
    if "paths" in openapi_schema:
        for path, path_item in openapi_schema["paths"].items():
            # Skip auth endpoints (login, callback)
            if "/auth/login" in path or "/auth/callback" in path:
                continue

            # Apply security to all methods in this path
            for method in path_item:
                if method in ["get", "post", "put", "delete", "patch"]:
                    # Add security requirement - Bearer token
                    path_item[method]["security"] = [
                        {"Bearer": []}
                    ]

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Add session middleware for OAuth2
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)


@app.on_event("startup")
def on_startup():
    """Create database tables on application startup (not when importing module)"""
    # Only create tables if not running tests
    if "pytest" not in sys.modules:
        Base.metadata.create_all(bind=engine)


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://kontracts-ui.vadlakonda.in", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1")
app.include_router(leases.router, prefix="/api/v1")
app.include_router(schedules.router, prefix="/api/v1")
app.include_router(payments.router, prefix="/api/v1")


@app.get("/")
def root():
    return {
        "message": "Lease Accounting API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}
