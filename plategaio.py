from datetime import datetime
from typing import Optional, Any, Dict
from uuid import UUID, uuid4

import httpx
from pydantic import BaseModel, Field, ConfigDict, ValidationError

class PlategaError(Exception):
    """base SDK error"""
    pass

class PlategaNetworkError(PlategaError):
    """rraised on network-related issues, like timeout"""
    pass

class PlategaAPIError(PlategaError):
    """raised when the API returns a non-200 response"""
    def __init__(self, status_code: int, message: str, response_body: Optional[Dict] = None):
        super().__init__(f"API Error {status_code}: {message}")
        self.status_code = status_code
        self.message = message
        self.response_body = response_body

class PaymentDetails(BaseModel):
    amount: float
    currency: str

class CreateTransactionRequest(BaseModel):
    payment_method: int = Field(..., alias="paymentMethod")
    id: UUID = Field(default_factory=uuid4)
    payment_details: PaymentDetails = Field(..., alias="paymentDetails")
    description: Optional[str] = None
    return_url: Optional[str] = Field(None, alias="returnUrl")
    failed_url: Optional[str] = Field(None, alias="failedUrl")
    payload: Optional[Any] = None

class CreateTransactionResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    transaction_id: str = Field(..., alias="transactionId")
    redirect: str
    status: str
    expires_in: Optional[str] = Field(None, alias="expiresIn")

class TransactionStatusResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    id: str
    status: str
    payment_details: Dict = Field(..., alias="paymentDetails")
    payment_method: str = Field(..., alias="paymentMethod")

class RateResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    rate: float
    updated_at: datetime = Field(..., alias="updatedAt")

class PlategaAsyncClient:
    """
    async platega.io SDK client.

    Args:
        merchant_id (str): Merchant ID (X-MerchantId header).
        secret (str): API key (X-Secret header).
        base_url (str): API base URL.
        timeout (int): Request timeout in seconds (default 15).
    """
    def __init__(
        self,
        merchant_id: str,
        secret: str,
        base_url: str = "https://app.platega.io",
        timeout: int = 15,
    ):
        self.merchant_id = merchant_id
        self.secret = secret
        self._session = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "X-MerchantId": str(self.merchant_id),
                "X-Secret": str(self.secret),
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            timeout=timeout,
        )

    async def __aenter__(self) -> "PlategaAsyncClient":
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.close()

    async def close(self) -> None:
        await self._session.aclose()

    async def _request(self, method: str, path: str, **kwargs) -> Dict:
        try:
            response = await self._session.request(method, path, **kwargs)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            response_body = e.response.json()
            msg = response_body.get("message", "unknown API error")
            raise PlategaAPIError(e.response.status_code, msg, response_body) from e
        except httpx.RequestError as e:
            raise PlategaNetworkError(f"request failed: {e}") from e
        except (ValueError, ValidationError) as e:
            raise PlategaError(f"failed to parse API response: {e}") from e

    async def create_transaction(self, payload: CreateTransactionRequest) -> CreateTransactionResponse:
        body = payload.model_dump(by_alias=True, exclude_none=True)
        body["id"] = str(body["id"])
        
        data = await self._request("POST", "/transaction/process", json=body)
        return CreateTransactionResponse.model_validate(data)

    async def get_transaction_status(self, transaction_id: str) -> TransactionStatusResponse:
        """fetch transaction status by its ID."""
        data = await self._request("GET", f"/transaction/{transaction_id}")
        return TransactionStatusResponse.model_validate(data)

    async def get_rate(self, payment_method: int, currency_from: str, currency_to: str) -> RateResponse:
        """get conversion rate for a payment method."""
        params = {
            "paymentMethod": payment_method,
            "currencyFrom": currency_from,
            "currencyTo": currency_to,
        }
        data = await self._request("GET", "/rates/payment_method_rate", params=params)
        return RateResponse.model_validate(data)
