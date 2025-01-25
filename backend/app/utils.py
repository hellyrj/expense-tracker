import requests

def fetch_currencies():
    url = 'https://v6.exchangerate-api.com/v6/ab97bd5614750d4db0b80557/latest/USD'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        if data['result'] == 'success':
            return list(data['conversion_rates'].keys())  # Extract currency codes
        else:
            return []  # Return an empty list if there's an error
    else:
        return []  # Return an empty list if the request fails
