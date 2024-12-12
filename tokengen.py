import requests

client_id = "141778"
client_secret = "a334c280c5e9cd771d1a4659b58ce9e2cfe183f4"
authorization_code = "f61e38659b043cf6170a1923cede5ad3bdf93547"

url = "https://www.strava.com/oauth/token"
payload = {
    "client_id": client_id,
    "client_secret": client_secret,
    "code": authorization_code,
    "grant_type": "authorization_code",
}

response = requests.post(url, data=payload)

if response.status_code == 200:
    tokens = response.json()
    print("Access Token:", tokens['access_token'])
    print("Refresh Token:", tokens['refresh_token'])
    print("Expire dans :", tokens['expires_in'], "secondes")
else:
    print("Erreur :", response.status_code, response.text)