import requests

url = "https://www.winners.mu/getFilteredProducts"

headers = {
    "User-Agent": "Mozilla/5.0",
    "X-Requested-With": "XMLHttpRequest"
}

response = requests.post(
    url,
    headers=headers,
    timeout=30
)

print("Status:", response.status_code)

print("\nResponse:")
print(response.text[:2000])