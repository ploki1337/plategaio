# 🟢 Platega SDK (Unofficial)

[![PyPI](https://img.shields.io/pypi/v/plategaio.svg)](https://pypi.org/project/plategaio/)  
[![Python](https://img.shields.io/pypi/pyversions/plategaio.svg)](https://pypi.org/project/plategaio/)  

> 🛠️ A simple and unofficial Python SDK for the [Platega.io](https://app.platega.io) API.  
> Provides convenient methods to create transactions, fetch statuses, and get rates.

---

## ✨ Features

- Minimalistic and clean API wrapper  
- Built-in request/response validation with **Pydantic**  
- Proper error handling with custom exceptions  
- Supports Python **3.8+**  

---

## 📦 Installation

```bash
pip install plategaio
```

---

## 🚀 Quick Start

```python
from plategaio import PlategaClient, CreateTransactionRequest, PaymentDetails
from uuid import uuid4

# init client
client = PlategaClient(
    merchant_id="YOUR_MERCHANT_ID",
    secret="YOUR_SECRET_KEY",
)

# create a transaction
tx = client.create_transaction(
    CreateTransactionRequest(
        paymentMethod=2,
        id=uuid4(),
        paymentDetails=PaymentDetails(amount=100.0, currency="RUB"),
        description="test order",
        return_url="https://your.site/success", # put your link after success payment
        failedUrl="https://your.site/failed", # put your link after failed payment
    )
)
print("Redirect user to:", tx.redirect)

# get transaction status
status = client.get_transaction_status(tx.transactionId)
print("Transaction status:", status.status)

# get conversion rate
rate = client.get_rate(payment_method=2, currency_from="USDT", currency_to="RUB")
print("USDT Rate:", rate.rate)
```

---

## ⚠️ Error Handling

SDK raises custom exceptions:

- `PlategaError` – Base exception  
- `PlategaHTTPError` – Non-200 API response  

Example:

```python
from plategaio import PlategaHTTPError

try:
    tx = client.create_transaction(...)
except PlategaHTTPError as e:
    print(f"Request failed: {e.status_code} {e.message}")
```

---

## 📚 API Reference

### `PlategaClient`
- `create_transaction(payload: CreateTransactionRequest) -> CreateTransactionResponse`  
- `get_transaction_status(transaction_id: str) -> TransactionStatusResponse`  
- `get_rate(payment_method: int, currency_from: str, currency_to: str, merchant_id: Optional[str] = None) -> RateResponse`

---

## 🌍 Links

- 📦 [PyPI](https://pypi.org/project/plategaio/)  
- 💻 [Source Code](https://github.com/ploki1337/plategaio)  
- 🔗 [Platega.io](https://app.platega.io)  
