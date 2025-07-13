import requests

def fetch_strava_activities(access_token, per_page=10):
    url = f"https://www.strava.com/api/v3/athlete/activities?per_page={per_page}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
