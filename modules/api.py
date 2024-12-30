import requests

class APIClient:
    def __init__(self, base_url='http://localhost:8000'):
        self.base_url = base_url

    def get(self, endpoint, params=None):
        response = requests.get(f"{self.base_url}/{endpoint}", params=params)
        return response.json()

    def post(self, endpoint, data=None):
        response = requests.post(f"{self.base_url}/{endpoint}", json=data)
        return response.json()

    def put(self, endpoint, data=None):
        response = requests.put(f"{self.base_url}/{endpoint}", json=data)
        return response.json()

    def delete(self, endpoint):
        response = requests.delete(f"{self.base_url}/{endpoint}")
        return response.json()

if __name__ == "__main__":
    client = APIClient()
    response = client.get('example-endpoint', params={'key': 'value'})
    print(response)