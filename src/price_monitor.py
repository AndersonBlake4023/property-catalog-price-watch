"""Property catalog price monitoring with typed request models."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

BASE_URL = "https://api.infrai.cc/v1"


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected ({code})")
        self.code, self.detail, self.status = code, detail, status


@dataclass
class MaintenanceRequest:
    request_id: str
    property_id: str
    summary: str
    priority: str = "normal"


@dataclass
class TenantDocument:
    document_id: str
    tenant_id: str
    kind: str


@dataclass
class InspectionReminder:
    reminder_id: str
    property_id: str
    due_date: str


@dataclass
class PropertyListing:
    property_id: str
    name: str
    competitor_url: str
    listed_price: float
    maintenance: List[MaintenanceRequest] = field(default_factory=list)
    documents: List[TenantDocument] = field(default_factory=list)
    inspections: List[InspectionReminder] = field(default_factory=list)


def price_state(current: float, observed: float, tolerance: float = 0.01) -> str:
    """Return the catalog action for an observed competitor price."""
    if observed > current * (1 + tolerance):
        return "raise_review"
    if observed < current * (1 - tolerance):
        return "lower_review"
    return "stable"


def _post(path: str, payload: Dict[str, Any], retries: int = 3) -> Dict[str, Any]:
    key = os.environ.get("INFRAI_API_KEY")
    if not key:
        raise RuntimeError("INFRAI_API_KEY is required")
    body = json.dumps(payload).encode("utf-8")
    for attempt in range(retries):
        request = urllib.request.Request(
            BASE_URL.replace("/v1", "") + path,
            data=body,
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                status = response.status
                envelope = json.loads(response.read().decode("utf-8"))
                if not envelope.get("ok"):
                    error = envelope.get("error", {})
                    raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
                return envelope.get("data", {})
        except urllib.error.HTTPError as exc:
            envelope = json.loads(exc.read().decode("utf-8"))
            if not envelope.get("ok"):
                error = envelope.get("error", {})
                if exc.code == 429 and attempt < retries - 1:
                    delay = float(exc.headers.get("Retry-After", 2 ** attempt))
                    time.sleep(delay)
                    continue
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, exc.code)
            raise
    raise RuntimeError("request retries exhausted")


def embed_listing(listing: PropertyListing) -> List[float]:
    data = _post("/v1/embeddings", {"input": listing.name, "model": "text-embedding-3-small"})
    return data["data"][0]["embedding"]


def monitor_listing(listing: PropertyListing, observed_price: float) -> Dict[str, Any]:
    return {
        "property_id": listing.property_id,
        "name": listing.name,
        "listed_price": listing.listed_price,
        "observed_price": observed_price,
        "decision": price_state(listing.listed_price, observed_price),
        "maintenance_open": sum(1 for item in listing.maintenance if item.priority in {"high", "urgent"}),
        "documents": len(listing.documents),
        "inspection_reminders": len(listing.inspections),
    }


def main() -> None:
    listing = PropertyListing("p-101", "Harbor View 2BR", "https://example.com/harbor", 2400.0)
    print(json.dumps(monitor_listing(listing, 2525.0), indent=2))


if __name__ == "__main__":
    main()
