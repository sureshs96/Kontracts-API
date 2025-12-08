# Zoho Directory OAuth2 Setup Guide

This guide explains how to configure Zoho Directory OAuth2 authentication for the Lease Accounting API.

## Zoho Application Configuration

### URLs to Configure in Zoho Application Console

When creating or editing your Zoho OAuth2 application, configure the following URLs:

#### 1. **Redirect URI (Required)**
This is where Zoho will redirect users after successful authentication:

**Local Development:**
```
http://localhost:8001/api/v1/auth/callback
```

**Production:**
```
https://your-api-domain.com/api/v1/auth/callback
```

#### 2. **Authorized JavaScript Origins (Optional)**
If you're using a frontend application:

**Local Development:**
```
http://localhost:3000
```

**Production:**
```
https://your-frontend-domain.com
```

#### 3. **Homepage URL**
```
http://localhost:8001
```
or
```
https://your-api-domain.com
```

---

## Step-by-Step Zoho Setup

### Step 1: Create a Zoho OAuth Application

1. Go to **[Zoho API Console](https://api-console.zoho.com/)**
2. Click **"Add Client"**
3. Choose **"Server-based Applications"**

### Step 2: Configure Application Details

Fill in the following information:

- **Client Name**: `Lease Accounting API`
- **Homepage URL**: `http://localhost:8001` (or your production URL)
- **Authorized Redirect URIs**: Add the callback URL(s) from above

### Step 3: Select Scopes

Select the following OAuth scopes:

- ✅ `openid` (Required)
- ✅ `profile` (Required)
- ✅ `email` (Required)
- ✅ `ZohoDirectory.users.READ` (Required for user info)

### Step 4: Get Your Credentials

After creating the application, you'll receive:

- **Client ID**: Copy this value
- **Client Secret**: Copy this value

### Step 5: Configure Environment Variables

Update your `.env` file with the credentials:

```bash
# Zoho OAuth2 Configuration
ZOHO_CLIENT_ID=1000.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
ZOHO_CLIENT_SECRET=your-secret-key-here
ZOHO_REDIRECT_URI=http://localhost:8001/api/v1/auth/callback
ZOHO_DOMAIN=accounts.zoho.com

# JWT Configuration
SECRET_KEY=generate-a-secure-random-key-at-least-32-characters-long
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

**Note:** For different Zoho data centers, use:
- 🇺🇸 US: `accounts.zoho.com`
- 🇪🇺 EU: `accounts.zoho.eu`
- 🇮🇳 India: `accounts.zoho.in`
- 🇦🇺 Australia: `accounts.zoho.com.au`
- 🇨🇳 China: `accounts.zoho.com.cn`
- 🇯🇵 Japan: `accounts.zoho.jp`

---

## API Endpoints

### Authentication Flow

#### 1. Initiate Login
```
GET /api/v1/auth/login
```
Redirects user to Zoho login page.

#### 2. OAuth Callback (Automatic)
```
GET /api/v1/auth/callback
```
Zoho redirects here after successful login.
Returns JWT token in JSON format.

#### 3. Get User Info
```
GET /api/v1/auth/me
Authorization: Bearer <your-jwt-token>
```
Returns authenticated user information.

#### 4. Logout
```
POST /api/v1/auth/logout
Authorization: Bearer <your-jwt-token>
```
Invalidates the JWT token (client-side deletion).

---

## Testing the Integration

### 1. Using Browser
1. Navigate to: `http://localhost:8001/api/v1/auth/login`
2. You'll be redirected to Zoho login page
3. Enter your Zoho credentials
4. After successful login, you'll be redirected back with a JWT token

### 2. Using Swagger UI
1. Go to: `http://localhost:8001/docs`
2. Click on `/api/v1/auth/login` endpoint
3. Click "Try it out" → "Execute"
4. Copy the redirect URL and open in browser
5. Complete Zoho login
6. Copy the `access_token` from the response
7. Click the "🔓 Authorize" button in Swagger UI
8. Enter the token: `Bearer <your-access-token>`
9. Now you can access all protected endpoints!

---

## Production Deployment Checklist

- [ ] Update `ZOHO_REDIRECT_URI` to production URL
- [ ] Generate a secure random `SECRET_KEY` (min 32 characters)
- [ ] Configure Zoho application with production redirect URI
- [ ] Set appropriate `ACCESS_TOKEN_EXPIRE_MINUTES` (recommended: 30-60)
- [ ] Use HTTPS for all URLs
- [ ] Add production domain to CORS `allow_origins`
- [ ] Store secrets securely (use environment variables, not in code)
- [ ] Enable Zoho OAuth consent screen customization
- [ ] Test the complete OAuth flow in production

---

## Troubleshooting

### "redirect_uri_mismatch" error
**Solution**: Ensure the redirect URI in your `.env` file exactly matches the one configured in Zoho Console (including http/https, trailing slashes, etc.)

### "invalid_client" error
**Solution**: Verify `ZOHO_CLIENT_ID` and `ZOHO_CLIENT_SECRET` are correct

### "invalid_scope" error
**Solution**: Ensure all required scopes are enabled in Zoho Console

### Token expires too quickly
**Solution**: Increase `ACCESS_TOKEN_EXPIRE_MINUTES` in `.env`

### CORS errors
**Solution**: Add your frontend URL to `allow_origins` in `app/main.py`

---

## Security Best Practices

1. **Never commit `.env` file** to version control
2. **Use strong SECRET_KEY** - Generate with:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
3. **Use HTTPS** in production
4. **Implement token refresh** for long-lived sessions
5. **Set appropriate token expiration** times
6. **Monitor OAuth logs** in Zoho Console
7. **Rotate secrets** periodically

---

## Additional Resources

- [Zoho OAuth2 Documentation](https://www.zoho.com/accounts/protocol/oauth.html)
- [Zoho API Console](https://api-console.zoho.com/)
- [Zoho Directory API](https://www.zoho.com/directory/help/api/)
