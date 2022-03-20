from google_auth_oauthlib.flow import Flow

google_api: Flow = Flow.from_client_secrets_file(
    'client_secret.json',
    scopes=[
        'openid',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile',
    ],
    redirect_uri='http://192.168.1.5:5000/api/oauth2/google',
)
