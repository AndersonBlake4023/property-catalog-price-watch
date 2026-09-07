import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from price_monitor import PropertyListing, monitor_listing, price_state


def test_competitor_increase_requests_review():
    listing = PropertyListing("p-1", "North Loop", "https://example.com/north", 1000.0)
    result = monitor_listing(listing, 1050.0)
    assert result["decision"] == "raise_review"
    assert price_state(1000, 995) == "stable"
