from typing import Optional, Any, Dict
import requests
from requests import Response
from pydantic import BaseModel, Field, ValidationError, ConfigDict
from uuid import UUID
import datetime


class PlategaError(Exception):
    """base sdk error"""
    pass


class PlategaHTTPError(PlategaError):
    """raised when API returns non-200 response"""
    def __init__(self, status_code: int, message: str, response: Optional[Dict] = None):
        super().__init__(f"HTTP {status_code}: {message}")
        self.status_code = status_code
        self.message = message
        self.response = response


class PaymentDetails(BaseModel):
    amount: float
    currency: str


class CreateTransactionRequest(BaseModel):
    paymentMethod: int
    id: UUID
    paymentDetails: PaymentDetails
    description: Optional[str] = None
    return_url: Optional[str] = Field(None, alias="return")
    failedUrl: Optional[str] = Field(None, alias="failedUrl")
    payload: Optional[Any] = None

    model_config = ConfigDict(validate_by_name=True, extra="allow")


class CreateTransactionResponse(BaseModel):
    paymentMethod: Optional[str]
    transactionId: Optional[str]
    redirect: Optional[str]
    return_url: Optional[str] = Field(None, alias="return")
    paymentDetails: Optional[str] = None
    status: Optional[str] = None
    expiresIn: Optional[str] = None
    merchantId: Optional[str] = None
    usdtRate: Optional[float] = None

    model_config = ConfigDict(validate_by_name=True, extra="allow")


class TransactionStatusResponse(BaseModel):
    id: Optional[str]
    status: Optional[str]
    paymentDetails: Optional[Dict] = None
    merchantName: Optional[str] = None
    mechantId: Optional[str] = None
    comission: Optional[float] = None
    paymentMethod: Optional[str] = None
    expiresIn: Optional[str] = None
    accountData: Optional[str] = None
    return_url: Optional[str] = Field(None, alias="return")

    model_config = ConfigDict(validate_by_name=True, extra="allow")


class RateResponse(BaseModel):
    paymentMethod: int
    currencyFrom: str
    currencyTo: str
    rate: float
    updatedAt: Optional[datetime.datetime] = None

    model_config = ConfigDict(extra="allow")


def _raise_for_response(resp: Response):
    if not resp.ok:
        try:
            data = resp.json()
            msg = data.get("message") or data
        except Exception:
            msg = resp.text or resp.reason
        raise PlategaHTTPError(resp.status_code, str(msg), response=getattr(resp, "text", None))


class PlategaClient:
    """
    Platega SDK client.

    Args:
        merchant_id (str): Merchant ID (X-MerchantId header).
        secret (str): API key (X-Secret header).
        timeout (int): Request timeout in seconds (default 15).
    """

    BASE_URL = "https://app.platega.io"

    def __init__(self, merchant_id: str, secret: str, timeout: int = 15):
        self.merchant_id = merchant_id
        self.secret = secret
        self.timeout = timeout
        self._session = requests.Session()
        self._session.headers.update({
            "X-MerchantId": str(self.merchant_id),
            "X-Secret": str(self.secret),
            "Content-Type": "application/json",
            "Accept": "application/json",
        })

    def create_transaction(self, payload: CreateTransactionRequest) -> CreateTransactionResponse:
        """create new transaction"""
        url = f"{self.BASE_URL}/transaction/process"
        body = payload.model_dump(by_alias=True, exclude_none=True)
        if isinstance(body.get("id"), UUID):
            body["id"] = str(body["id"])

        resp = self._session.post(url, json=body, timeout=self.timeout)
        _raise_for_response(resp)
        data = resp.json()

        try:
            return CreateTransactionResponse.model_validate(data)
        except ValidationError:
            return CreateTransactionResponse(**data)

    def get_transaction_status(self, transaction_id: str) -> TransactionStatusResponse:
        """fetch transaction status by id"""
        url = f"{self.BASE_URL}/transaction/{transaction_id}"
        resp = self._session.get(url, timeout=self.timeout)
        _raise_for_response(resp)
        data = resp.json()

        try:
            return TransactionStatusResponse.model_validate(data)
        except ValidationError:
            return TransactionStatusResponse(**data)

    def get_rate(self, payment_method: int, currency_from: str, currency_to: str, merchant_id: Optional[str] = None) -> RateResponse:
        """get conversion rate for payment method"""
        url = f"{self.BASE_URL}/rates/payment_method_rate"
        params = {
            "merchantId": merchant_id or self.merchant_id,
            "paymentMethod": payment_method,
            "currencyFrom": currency_from,
            "currencyTo": currency_to,
        }

        resp = self._session.get(url, params=params, timeout=self.timeout)
        _raise_for_response(resp)
        data = resp.json()

        try:
            return RateResponse.model_validate(data)
        except ValidationError:
            return RateResponse(**data)