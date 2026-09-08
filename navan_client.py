"""Official Navan REST API client with error classification and secret sanitization."""
from __future__ import annotations
import httpx
from typing import Any, Optional

DEFAULT_NAVAN_BASE = "https://api.navan.com"

class NavanClient:
    def __init__(self, api_key: str, base_url: str = ""):
        self.api_key = api_key.strip()
        self.base_url = (base_url.strip() if base_url else DEFAULT_NAVAN_BASE).rstrip("/")
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Imperal-Navan/0.1.0"
        }
        self.timeout = httpx.Timeout(30.0, connect=10.0)

    def _sanitize_msg(self, msg: str) -> str:
        if not msg:
            return ""
        if self.api_key and len(self.api_key) > 6:
            msg = msg.replace(self.api_key, self.api_key[:3] + "..." + self.api_key[-3:])
        return msg

    def _classify_error(self, resp: httpx.Response, action_name: str) -> dict[str, Any]:
        status = resp.status_code
        err_msg = ""
        try:
            data = resp.json()
            if "errors" in data and isinstance(data["errors"], list) and len(data["errors"]) > 0:
                err_msg = "; ".join(e.get("message", "") for e in data["errors"])
            elif "message" in data:
                err_msg = data["message"]
            elif "error" in data:
                err_msg = str(data["error"])
        except Exception:
            err_msg = resp.text[:200]
        err_msg = self._sanitize_msg(err_msg)

        if status == 429:
            retry_after = resp.headers.get("Retry-After", "60")
            return {
                "status": "error",
                "code": "RATE_LIMITED",
                "message": f"Navan API rate limit exceeded during {action_name}. Retry after {retry_after}s. Details: {err_msg}",
                "retry_after": int(retry_after) if retry_after.isdigit() else 60
            }
        elif status == 401:
            return {
                "status": "error",
                "code": "UNAUTHORIZED",
                "message": f"Invalid or expired Navan API key for {action_name}. Details: {err_msg}"
            }
        elif status == 403:
            return {
                "status": "error",
                "code": "FORBIDDEN",
                "message": f"Permission denied for Navan {action_name}. Check your API token scopes. Details: {err_msg}"
            }
        elif status == 404:
            return {
                "status": "error",
                "code": "NOT_FOUND",
                "message": f"Navan resource not found in {action_name}. Details: {err_msg}"
            }
        return {
            "status": "error",
            "code": f"HTTP_{status}",
            "message": f"Navan API error ({status}) during {action_name}: {err_msg}"
        }

    async def verify_auth(self) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.get(f"{self.base_url}/v1/users/me", headers=self.headers)
                if resp.status_code in (200, 201):
                    return {"status": "ok", "data": resp.json()}
                if resp.status_code in (401, 403):
                    return self._classify_error(resp, "verify_auth")
                # fallback check
                resp2 = await client.get(f"{self.base_url}/v1/expenses", headers=self.headers, params={"limit": 1})
                if resp2.status_code in (200, 201):
                    return {"status": "ok", "data": resp2.json()}
                return self._classify_error(resp2, "verify_auth")
            except httpx.RequestError as exc:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(f"Network error connecting to Navan: {str(exc)}")}

    async def _request(self, method: str, path: str, action_name: str, params: dict = None, json_body: dict = None) -> dict[str, Any]:
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                resp = await client.request(method, url, headers=self.headers, params=params, json=json_body)
                if resp.status_code in (200, 201):
                    return {"status": "ok", "data": resp.json() if resp.content else {}}
                elif resp.status_code == 204:
                    return {"status": "ok", "data": {"deleted": True}}
                return self._classify_error(resp, action_name)
            except httpx.RequestError as exc:
                return {"status": "error", "code": "CONNECTION_ERROR", "message": self._sanitize_msg(f"Network error during {action_name}: {str(exc)}")}

    async def list_expenses(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        p = {"limit": min(limit, 100)}
        if cursor: p["cursor"] = cursor
        return await self._request("GET", "/v1/expenses", "list_expenses", params=p)

    async def get_expense(self, item_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/v1/expenses/{item_id}", "get_expense")

    async def create_expense(self, data: dict[str, Any] = None, name: str = "", details: dict[str, Any] = None, **kwargs) -> dict[str, Any]:
        if data is None: data = {"name": name, **(details or {})}
        return await self._request("POST", "/v1/expenses", "create_expense", json_body=data)

    async def update_expense(self, item_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._request("PATCH", f"/v1/expenses/{item_id}", "update_expense", json_body=data)

    async def delete_expense(self, item_id: str) -> dict[str, Any]:
        return await self._request("DELETE", f"/v1/expenses/{item_id}", "delete_expense")

    async def list_cards(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        p = {"limit": min(limit, 100)}
        if cursor: p["cursor"] = cursor
        return await self._request("GET", "/v1/cards", "list_cards", params=p)

    async def get_card(self, item_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/v1/cards/{item_id}", "get_card")

    async def create_card(self, data: dict[str, Any] = None, name: str = "", details: dict[str, Any] = None, **kwargs) -> dict[str, Any]:
        if data is None: data = {"name": name, **(details or {})}
        return await self._request("POST", "/v1/cards", "create_card", json_body=data)

    async def update_card(self, item_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._request("PATCH", f"/v1/cards/{item_id}", "update_card", json_body=data)

    async def delete_card(self, item_id: str) -> dict[str, Any]:
        return await self._request("DELETE", f"/v1/cards/{item_id}", "delete_card")

    async def list_reports(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        p = {"limit": min(limit, 100)}
        if cursor: p["cursor"] = cursor
        return await self._request("GET", "/v1/reports", "list_reports", params=p)

    async def get_report(self, item_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/v1/reports/{item_id}", "get_report")

    async def create_report(self, data: dict[str, Any] = None, name: str = "", details: dict[str, Any] = None, **kwargs) -> dict[str, Any]:
        if data is None: data = {"name": name, **(details or {})}
        return await self._request("POST", "/v1/reports", "create_report", json_body=data)

    async def update_report(self, item_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._request("PATCH", f"/v1/reports/{item_id}", "update_report", json_body=data)

    async def delete_report(self, item_id: str) -> dict[str, Any]:
        return await self._request("DELETE", f"/v1/reports/{item_id}", "delete_report")

    async def list_policies(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        p = {"limit": min(limit, 100)}
        if cursor: p["cursor"] = cursor
        return await self._request("GET", "/v1/policies", "list_policies", params=p)

    async def get_policy(self, item_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/v1/policies/{item_id}", "get_policy")

    async def create_policy(self, data: dict[str, Any] = None, name: str = "", details: dict[str, Any] = None, **kwargs) -> dict[str, Any]:
        if data is None: data = {"name": name, **(details or {})}
        return await self._request("POST", "/v1/policies", "create_policy", json_body=data)

    async def update_policy(self, item_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._request("PATCH", f"/v1/policies/{item_id}", "update_policy", json_body=data)

    async def delete_policy(self, item_id: str) -> dict[str, Any]:
        return await self._request("DELETE", f"/v1/policies/{item_id}", "delete_policy")

    async def list_merchants(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        p = {"limit": min(limit, 100)}
        if cursor: p["cursor"] = cursor
        return await self._request("GET", "/v1/merchants", "list_merchants", params=p)

    async def get_merchant(self, item_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/v1/merchants/{item_id}", "get_merchant")

    async def create_merchant(self, data: dict[str, Any] = None, name: str = "", details: dict[str, Any] = None, **kwargs) -> dict[str, Any]:
        if data is None: data = {"name": name, **(details or {})}
        return await self._request("POST", "/v1/merchants", "create_merchant", json_body=data)

    async def update_merchant(self, item_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._request("PATCH", f"/v1/merchants/{item_id}", "update_merchant", json_body=data)

    async def delete_merchant(self, item_id: str) -> dict[str, Any]:
        return await self._request("DELETE", f"/v1/merchants/{item_id}", "delete_merchant")

    async def list_reimbursements(self, limit: int = 50, cursor: str = "") -> dict[str, Any]:
        p = {"limit": min(limit, 100)}
        if cursor: p["cursor"] = cursor
        return await self._request("GET", "/v1/reimbursements", "list_reimbursements", params=p)

    async def get_reimbursement(self, item_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/v1/reimbursements/{item_id}", "get_reimbursement")

    async def create_reimbursement(self, data: dict[str, Any] = None, name: str = "", details: dict[str, Any] = None, **kwargs) -> dict[str, Any]:
        if data is None: data = {"name": name, **(details or {})}
        return await self._request("POST", "/v1/reimbursements", "create_reimbursement", json_body=data)

    async def update_reimbursement(self, item_id: str, data: dict[str, Any]) -> dict[str, Any]:
        return await self._request("PATCH", f"/v1/reimbursements/{item_id}", "update_reimbursement", json_body=data)

    async def delete_reimbursement(self, item_id: str) -> dict[str, Any]:
        return await self._request("DELETE", f"/v1/reimbursements/{item_id}", "delete_reimbursement")

    async def audit_spend_compliance(self) -> dict[str, Any]:
        res = await self.list_expenses(limit=100)
        if res.get("status") == "error":
            return res
        items = res.get("data", {}).get("items", []) if isinstance(res.get("data"), dict) else []
        violations = []
        for exp in items:
            if exp.get("flagged") or exp.get("policy_violation"):
                violations.append(exp)
        return {
            "status": "ok",
            "data": {
                "total_expenses_scanned": len(items),
                "violations_found": len(violations),
                "compliant": len(violations) == 0,
                "flagged_items": violations
            }
        }

    async def get_spend_overview(self) -> dict[str, Any]:
        res = await self.list_expenses(limit=100)
        if res.get("status") == "error":
            return res
        items = res.get("data", {}).get("items", []) if isinstance(res.get("data"), dict) else []
        total_amount = sum(float(exp.get("amount", 0)) for exp in items if isinstance(exp, dict))
        by_cat = {}
        for exp in items:
            cat = exp.get("category", "Uncategorized")
            by_cat[cat] = by_cat.get(cat, 0.0) + float(exp.get("amount", 0))
        return {
            "status": "ok",
            "data": {
                "total_spend": total_amount,
                "transactions_count": len(items),
                "by_category": by_cat
            }
        }
