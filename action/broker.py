from __future__ import annotations

import os
import pathlib
from dataclasses import dataclass
from typing import Optional, Dict, Any
from dotenv import load_dotenv

import robin_stocks.robinhood as r

load_dotenv()

@dataclass
class RobinhoodClient:
    username: Optional[str] = None
    password: Optional[str] = None
    mfa_code: Optional[str] = None
    device_token_path: pathlib.Path = pathlib.Path.home() / ".rh_device_token"

    _logged_in: bool = False


    def login(self, store_session: bool = True) -> Dict[str, Any]:
        """Authenticate and cache the session token.

        Must be called **once** before any other operation. Returns the
        raw response from ``robin_stocks`` so you can inspect it if
        needed.
        """
        self._ensure_credentials()

        # Try to reuse a previously saved device‑token to avoid MFA/SMS.
        device_token = (
            self.device_token_path.read_text().strip()
            if self.device_token_path.exists()
            else None
        )

        login_resp = r.login(
            self.username,  
            self.password,  
            mfa_code=self.mfa_code or os.getenv("RH_MFA_CODE"),
            store_session=store_session,
            expiresIn=60 * 60 * 24,  
            device_token=device_token,
        )

        # Persist newly issued device‑token for next time.
        new_token = login_resp.get("device_token")
        if new_token and new_token != device_token:
            self.device_token_path.write_text(new_token)

        self._logged_in = True
        return login_resp

    def logout(self) -> None:
        """Invalidate session."""
        if self._logged_in:
            r.logout()
            self._logged_in = False

    def get_quote(self, symbol: str, extended: bool = False) -> float:
        """Return *latest* price for *symbol* as ``float`` (USD)."""
        self._ensure_login()
        price = r.get_latest_price(symbol, includeExtendedHours=extended)
        if not price or not price[0]:
            raise RuntimeError(f"Quote for {symbol} unavailable.")
        return float(price[0])

    def buy(
        self,
        symbol: str,
        quantity: int,
        order_type: str = "market",  # "market" | "limit"
        time_in_force: str = "gfd",  # "gfd" | "gtc"
        price: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Place a *buy* order and return Robinhood’s JSON response."""
        self._ensure_login()
        if order_type == "market":
            return r.order_buy_market(symbol, quantity, timeInForce=time_in_force)
        if order_type == "limit":
            if price is None:
                raise ValueError("Limit orders require *price* argument.")
            return r.order_buy_limit(symbol, quantity, price, timeInForce=time_in_force)
        raise ValueError("order_type must be 'market' or 'limit'.")

    def sell(
        self,
        symbol: str,
        quantity: int,
        order_type: str = "market",
        time_in_force: str = "gfd",
        price: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Place a *sell* order."""
        self._ensure_login()
        if order_type == "market":
            return r.order_sell_market(symbol, quantity, timeInForce=time_in_force)
        if order_type == "limit":
            if price is None:
                raise ValueError("Limit orders require *price* argument.")
            return r.order_sell_limit(symbol, quantity, price, timeInForce=time_in_force)
        raise ValueError("order_type must be 'market' or 'limit'.")

    def get_positions(self) -> Dict[str, Any]:
        """Return *dict* keyed by ticker of current holdings."""
        self._ensure_login()
        return r.build_holdings()

    def _ensure_credentials(self) -> None:
        self.username = self.username or os.getenv("RH_USERNAME")
        self.password = self.password or os.getenv("RH_PASSWORD")
        if not self.username or not self.password:
            raise RuntimeError(
                "Missing Robinhood credentials. Set RH_USERNAME / RH_PASSWORD."\
            )

    def _ensure_login(self) -> None:
        if not self._logged_in:
            raise RuntimeError("Call .login() before API methods.")
