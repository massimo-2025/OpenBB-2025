# Remote User Access Guide

This document explains how users can connect to your OpenBB ODP instance.

## Connection Methods

### Python Client

```python
from openbb import obb

# Configure the remote API endpoint
import os
os.environ["OPENBB_API_URL"] = "http://your-server-ip:6900"

# Or use requests directly
import requests

BASE_URL = "http://your-server-ip:6900/api/v1"

# Get stock quote
response = requests.get(f"{BASE_URL}/equity/price/quote", params={"symbol": "AAPL"})
data = response.json()
print(data)

# Get historical data
response = requests.get(
    f"{BASE_URL}/equity/price/historical",
    params={
        "symbol": "AAPL",
        "start_date": "2024-01-01",
        "end_date": "2024-12-31"
    }
)
```

### JavaScript/TypeScript

```javascript
const API_URL = 'http://your-server-ip:6900/api/v1';

// Fetch stock quote
async function getQuote(symbol) {
    const response = await fetch(`${API_URL}/equity/price/quote?symbol=${symbol}`);
    return response.json();
}

// Example usage
getQuote('AAPL').then(data => console.log(data));
```

### cURL

```bash
# Get stock quote
curl "http://your-server-ip:6900/api/v1/equity/price/quote?symbol=AAPL"

# Get historical data
curl "http://your-server-ip:6900/api/v1/equity/price/historical?symbol=AAPL&start_date=2024-01-01"
```

## Available Endpoints

Visit `http://your-server-ip:6900/docs` for the full OpenAPI documentation.

### Common Endpoints

| Endpoint | Description |
|----------|-------------|
| `/api/v1/equity/price/quote` | Get stock quotes |
| `/api/v1/equity/price/historical` | Historical price data |
| `/api/v1/equity/fundamental/income` | Income statements |
| `/api/v1/equity/fundamental/balance` | Balance sheets |
| `/api/v1/crypto/price/historical` | Crypto historical data |
| `/api/v1/economy/gdp` | GDP data |
| `/api/v1/news/company` | Company news |

## Authentication (if enabled)

If the server requires authentication, include headers:

```python
headers = {
    "Authorization": "Bearer YOUR_TOKEN"
}
response = requests.get(url, headers=headers)
```

## Rate Limits

Default rate limits (configurable by admin):
- 100 requests per minute per IP
- 1000 requests per hour per IP

## Error Handling

```python
response = requests.get(f"{BASE_URL}/equity/price/quote", params={"symbol": "AAPL"})

if response.status_code == 200:
    data = response.json()
elif response.status_code == 429:
    print("Rate limited - wait and retry")
elif response.status_code == 401:
    print("Authentication required")
else:
    print(f"Error: {response.status_code}")
```

## Best Practices

1. **Cache responses** when possible to reduce API calls
2. **Use batch requests** for multiple symbols when available
3. **Implement retry logic** with exponential backoff
4. **Store credentials securely** - never commit API keys to version control
