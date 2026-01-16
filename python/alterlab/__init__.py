"""
AlterLab Python SDK - Official client for the AlterLab Web Scraping API.

Simple Example:
    from alterlab import AlterLab

    client = AlterLab(api_key="sk_live_...")
    result = client.scrape("https://example.com")
    print(result.text)

Async Example:
    from alterlab import AsyncAlterLab

    async with AsyncAlterLab(api_key="sk_live_...") as client:
        result = await client.scrape("https://example.com")
        print(result.text)

Documentation: https://alterlab.io/docs
"""

from alterlab.client import (
    # Main clients
    AlterLab,
    AsyncAlterLab,
    # Options
    AdvancedOptions,
    CostControls,
    # Results
    ScrapeResult,
    CostEstimate,
    UsageStats,
    JobStatus,
    BillingDetails,
    TierEscalation,
    # Exceptions
    AlterLabError,
    AlterLabAPIError,
    AuthenticationError,
    InsufficientCreditsError,
    RateLimitError,
    ValidationError,
    ScrapeError,
    TimeoutError,
    # Version
    __version__,
)

__all__ = [
    # Clients
    "AlterLab",
    "AsyncAlterLab",
    # Options
    "AdvancedOptions",
    "CostControls",
    # Results
    "ScrapeResult",
    "CostEstimate",
    "UsageStats",
    "JobStatus",
    "BillingDetails",
    "TierEscalation",
    # Exceptions
    "AlterLabError",
    "AlterLabAPIError",
    "AuthenticationError",
    "InsufficientCreditsError",
    "RateLimitError",
    "ValidationError",
    "ScrapeError",
    "TimeoutError",
    # Version
    "__version__",
]
