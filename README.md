# 🟢 Platega Async SDK (Unofficial)

[![PyPI](https://img.shields.io/pypi/v/plategaio-async.svg)](https://pypi.org/project/plategaio/)
[![Python](https://img.shields.io/pypi/pyversions/plategaio-async.svg)](https://pypi.org/project/plategaio/)
[![License](https://img.shields.io/pypi/l/plategaio-async.svg)](https://github.com/ploki1337/plategaio/blob/main/LICENSE)

> 🛠️ A modern, unofficial **asynchronous** Python SDK for the [Platega.io](https://platega.io) API.  
> Built with `httpx` and `Pydantic` for high performance in async applications like `aiogram`, `FastAPI`, or `Django Ninja`.

---

## ✨ Features

-   **Fully Asynchronous**: Built with `httpx` to be non-blocking and perfect for modern async frameworks.
-   **Type-Safe**: Strict request/response validation with Pydantic V2 ensures your code is robust.
-   **Secure by Default**: Includes a helper to verify webhook signatures, protecting you from fake callbacks.
-   **Clean API**: A minimalistic and intuitive interface for creating transactions, fetching statuses, and getting rates.
-   **Robust Error Handling**: Clear, custom exceptions for network and API errors.
-   **Resource Management**: Uses an async context manager (`async with`) to handle client sessions gracefully.
-   **Modern Python**: Supports Python 3.8+.

---

## 📦 Installation

```bash
pip install plategaio
```

---

## 🚀 Quick Start

The client is designed to be used as an asynchronous context manager.

```python
import asyncio
from uuid import uuid4
from plategaio import (
    PlategaAsyncClient,
    CreateTransactionRequest,
    PaymentDetails,
    PlategaAPIError,
)

async def main():
    async with PlategaAsyncClient(
        merchant_id="YOUR_MERCHANT_ID",
        secret="YOUR_SECRET_KEY",
    ) as client:
        try:
            tx_request = CreateTransactionRequest(
                payment_method=2, # SBP
                id=uuid4(),
                payment_details=PaymentDetails(amount=150.50, currency="RUB"),
                description="Order #123",
                return_url="https://your.site/success",
                failed_url="https://your.site/failed",
            )
            tx_response = await client.create_transaction(tx_request)
            print(f"Redirect user to: {tx_response.redirect}")
            
            status = await client.get_transaction_status(tx_response.transaction_id)
            print(f"Transaction status: {status.status}")

            rate = await client.get_rate(
                payment_method=2, 
                currency_from="USDT", 
                currency_to="RUB"
            )
            print(f"Current USDT->RUB rate: {rate.rate}")

        except PlategaAPIError as e:
            print(f"API Error: {e.status_code} - {e.message}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## ⚠️ Error Handling

The SDK raises clear, specific exceptions:

-   `PlategaError`: Base exception for the library.
-   `PlategaNetworkError`: Raised for network issues like timeouts or connection errors.
-   `PlategaAPIError`: Raised for non-2xx API responses (e.g., 400, 401, 500). It contains `status_code`, `message`, and `response_body`.

Example:

```python
from plategaio import PlategaAPIError, PlategaNetworkError

try:
    # ... your API call
except PlategaAPIError as e:
    print(f"API returned an error: status={e.status_code}, message='{e.message}'")
except PlategaNetworkError as e:
    print(f"A network error occurred: {e}")
```

---

## 📚 API Reference

### `PlategaAsyncClient`

-   `async create_transaction(payload: CreateTransactionRequest) -> CreateTransactionResponse`
-   `async get_transaction_status(transaction_id: str) -> TransactionStatusResponse`
-   `async get_rate(payment_method: int, currency_from: str, currency_to: str) -> RateResponse`
-   `async close()`: Closes the client session. Called automatically when using `async with`.

---

## 🌍 Links

-   📦 [PyPI](https://pypi.org/project/plategaio/)
-   💻 [Source Code](https://github.com/ploki1337/plategaio)
-   🔗 [Platega.io](https://platega.io)
