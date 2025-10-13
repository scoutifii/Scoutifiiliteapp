import requests


def fetch_radio_stations(country):
    url = "https://de1.api.radio-browser.info/json/stations/bycountry"
    params = {"country": country}
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        return []


stations = fetch_radio_stations("United States")
for station in stations[:5]:  # Limit to 5 stations for testing
    print(f"Station: {station['name']}, Stream URL: {station['url']}")