import requests
url = "http://example.com"
response = requests.get(url)
class RivaAuthMixin:
    """Configuration for the authentication to a Riva service connection."""
    examples=["http://localhost:50051", "https://user@pass:riva.example.com"]
