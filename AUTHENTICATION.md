# Authentication (Zoho Directory + JWT)

The API uses Zoho Directory OAuth2 for sign-in and then issues a short-lived JWT for subsequent requests.

## Flow
- `GET /api/v1/auth/login`: redirect to Zoho for consent.
- `GET /api/v1/auth/callback`: exchanges the code, fetches user info, and returns a JWT.
- `GET /api/v1/auth/me`: verify the JWT and return the user claims.
- `POST /api/v1/auth/logout`: validates the token and responds with a logout message (clients delete the token).

## Configuration
Set these environment variables (see `.env.example`):
```
ZOHO_CLIENT_ID=<your-client-id>
ZOHO_CLIENT_SECRET=<your-client-secret>
ZOHO_REDIRECT_URI=http://localhost:8001/api/v1/auth/callback
ZOHO_DOMAIN=accounts.zoho.com           # or .eu, .in, etc.
SECRET_KEY=<jwt-signing-key>
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Using the token
1) Hit `/api/v1/auth/login` in the browser and complete Zoho auth.  
2) Copy the `access_token` returned by `/api/v1/auth/callback`.  
3) Send it as `Authorization: Bearer <token>` to protected endpoints or via the 🔓 Authorize button in Swagger UI.

### Logout
- `POST /api/v1/auth/logout` revokes the Zoho access token via Zoho's `oauth/v2/token/revoke` endpoint and invalidates the JWT (process-local; uses `jti` if present, otherwise hashes the raw token). Clients should still discard the token. For multi-instance deployments, back the JWT revocation store with shared infra (e.g., Redis).
