import requests
import json
from urllib.parse import urlencode

file = open('client_secret.json')
creds = json.load(file)

CLIENT_ID = creds['installed']['client_id']
CLIENT_SECRET = creds['installed']['client_secret']
REDIRECT_URI = creds['installed']['redirect_uris']
SCOPE = 'https://www.googleapis.com/auth/photoslibrary'

AUTH_URL = 'https://accounts.google.com/o/oauth2/auth'
TOKEN_URL = 'https://oauth2.googleapis.com/token'


def get_authorization_url():
    params = {
        'client_id': CLIENT_ID,
        'redirect_uri': REDIRECT_URI,
        'scope': SCOPE,
        'response_type': 'code'
    }
    return f"{AUTH_URL}?{urlencode(params)}"


def exchange_code_for_token(code):
    data = {
        'code': code,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'redirect_uri': REDIRECT_URI,
        'grant_type': 'authorization_code'
    }
    response = requests.post(TOKEN_URL, data=data)
    return response.json()


def save_tokens(tokens):
    with open('token.json', 'w') as f:
        json.dump(tokens, f)


def load_tokens():
    try:
        with open('token.json', 'r') as f:
            tokens = json.load(f)
        return tokens
    except FileNotFoundError:
        return None


def refresh_token(refresh_token):
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token'
    }
    response = requests.post(TOKEN_URL, data=data)
    return response.json()


def fetch_photos(access_token):
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json'
    }
    response = requests.get('https://photoslibrary.googleapis.com/v1/albums', headers=headers)
    return response.json()


if __name__ == '__main__':
    tokens = load_tokens()

    if tokens and 'access_token' in tokens:
        access_token = tokens['access_token']
        print("Using existing access token.")

    else:
        print("Go to the following URL and authorize access:")
        print(get_authorization_url())

        code = input("Enter the authorization code from the redirect URL: ")

        tokens = exchange_code_for_token(code)

        if 'access_token' in tokens:
            access_token = tokens['access_token']
            save_tokens(tokens)
            print("Access token obtained and saved.")
        else:
            print("Failed to retrieve access token.")
            print(tokens)
            exit()

    photos = fetch_photos(access_token)
    print("Photos in the album:")
    print(photos)

    if 'refresh_token' in tokens:
        refreshed_tokens = refresh_token(tokens['refresh_token'])
        if 'access_token' in refreshed_tokens:
            tokens['access_token'] = refreshed_tokens['access_token']
            save_tokens(tokens)
            print("Access token refreshed and saved.")
