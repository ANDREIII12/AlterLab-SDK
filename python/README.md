# AlterLab Python SDK

Official Python SDK for the [AlterLab Web Scraping API](https://alterlab.io). Extract data from any website with intelligent anti-bot bypass, JavaScript rendering, and structured extraction.

[![PyPI version](https://badge.fury.io/py/alterlab.svg)](https://badge.fury.io/py/alterlab)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Simple API**: 3 lines of code to scrape any website
- **Intelligent Anti-Bot Bypass**: Automatic tier escalation (curl → HTTP → stealth → browser)
- **JavaScript Rendering**: Full Playwright browser for JS-heavy sites
- **Structured Extraction**: JSON Schema, prompts, and pre-built profiles
- **BYOP Support**: Bring Your Own Proxy for 20% discount
- **Async Support**: Native asyncio for concurrent scraping
- **Type Hints**: Full typing support for IDE autocomplete
- **Cost Controls**: Set budgets, prefer cost/speed, fail-fast options

## Installation

```bash
pip install alterlab
```

## Quick Start

```python
from alterlab import AlterLab

# Initialize client
client = AlterLab(api_key="sk_live_...")  # or set ALTERLAB_API_KEY env var

# Scrape a website
result = client.scrape("https://example.com")
print(result.text)          # Extracted text
print(result.json)          # Structured JSON (Schema.org, metadata)
print(result.billing.cost_dollars)  # Cost breakdown
```

## Pricing

Pay-as-you-go pricing with no subscriptions. **$1 = 5,000 scrapes** (Tier 1).

| Tier | Name | Price | Per $1 | Use Case |
|------|------|-------|--------|----------|
| 1 | Curl | $0.0002 | 5,000 | Static HTML sites |
| 2 | HTTP | $0.0003 | 3,333 | Sites with TLS fingerprinting |
| 3 | Stealth | $0.0005 | 2,000 | Sites with browser checks |
| 4 | Browser | $0.001 | 1,000 | JS-heavy SPAs |
| 5 | Captcha | $0.02 | 50 | Sites with CAPTCHAs |

The API automatically escalates through tiers until successful, charging only for the tier used.

## Usage Examples

### Basic Scraping

```python
from alterlab import AlterLab

client = AlterLab(api_key="sk_live_...")

# Auto mode - intelligent tier escalation
result = client.scrape("https://example.com")

# Force HTML-only (fastest, cheapest)
result = client.scrape_html("https://example.com")

# JavaScript rendering
result = client.scrape_js("https://spa-app.com", screenshot=True)
print(result.screenshot_url)
```

### Structured Extraction

```python
# Extract specific fields with JSON Schema
result = client.scrape(
    "https://store.com/product/123",
    extraction_schema={
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "price": {"type": "number"},
            "in_stock": {"type": "boolean"}
        }
    }
)
print(result.json)  # {"name": "...", "price": 29.99, "in_stock": true}

# Or use a pre-built profile
result = client.scrape(
    "https://store.com/product/123",
    extraction_profile="product"
)
```

### Cost Controls

```python
from alterlab import AlterLab, CostControls

client = AlterLab(api_key="sk_live_...")

# Limit to cheap tiers only
result = client.scrape(
    "https://example.com",
    cost_controls=CostControls(
        max_tier="2",       # Don't go above HTTP tier
        prefer_cost=True,   # Optimize for lowest cost
        fail_fast=True      # Error instead of escalating
    )
)

# Estimate cost before scraping
estimate = client.estimate_cost("https://linkedin.com")
print(f"Estimated: ${estimate.estimated_cost_dollars:.4f}")
print(f"Confidence: {estimate.confidence}")
```

### Advanced Options

```python
from alterlab import AlterLab, AdvancedOptions

client = AlterLab(api_key="sk_live_...")

# Full browser with screenshot and PDF
result = client.scrape(
    "https://example.com",
    mode="js",
    advanced=AdvancedOptions(
        render_js=True,
        screenshot=True,
        generate_pdf=True,
        markdown=True,
        wait_condition="networkidle"
    )
)

print(result.screenshot_url)
print(result.pdf_url)
print(result.markdown_content)
```

### BYOP (Bring Your Own Proxy)

Get 20% discount when using your own proxy:

```python
from alterlab import AlterLab, AdvancedOptions

client = AlterLab(api_key="sk_live_...")

# Use your configured proxy integration
result = client.scrape(
    "https://example.com",
    advanced=AdvancedOptions(
        use_own_proxy=True,
        proxy_country="US"  # Optional: request specific geo
    )
)

# Check if BYOP was applied
if result.billing.byop_applied:
    print(f"Saved {result.billing.byop_discount_percent}%!")
```

### Async Support

```python
import asyncio
from alterlab import AsyncAlterLab

async def main():
    async with AsyncAlterLab(api_key="sk_live_...") as client:
        # Single request
        result = await client.scrape("https://example.com")

        # Concurrent requests
        urls = [
            "https://example.com/page1",
            "https://example.com/page2",
            "https://example.com/page3",
        ]
        results = await asyncio.gather(*[client.scrape(url) for url in urls])

        for r in results:
            print(r.title, r.billing.cost_dollars)

asyncio.run(main())
```

### Caching

```python
# Enable caching (opt-in)
result = client.scrape(
    "https://example.com",
    cache=True,          # Enable caching
    cache_ttl=3600,      # Cache for 1 hour
)

if result.cached:
    print("Cache hit - no credits charged!")

# Force refresh
result = client.scrape(
    "https://example.com",
    cache=True,
    force_refresh=True   # Bypass cache
)
```

### PDF and Image Extraction

```python
# Extract text from PDF
result = client.scrape_pdf(
    "https://example.com/document.pdf",
    format="markdown"
)
print(result.text)

# OCR for images
result = client.scrape_ocr(
    "https://example.com/image.png",
    language="eng"
)
print(result.text)
```

### Error Handling

```python
from alterlab import (
    AlterLab,
    AuthenticationError,
    InsufficientCreditsError,
    RateLimitError,
    ScrapeError,
    TimeoutError
)

client = AlterLab(api_key="sk_live_...")

try:
    result = client.scrape("https://example.com")
except AuthenticationError:
    print("Invalid API key")
except InsufficientCreditsError:
    print("Please top up your balance")
except RateLimitError as e:
    print(f"Rate limited. Retry after {e.retry_after}s")
except ScrapeError as e:
    print(f"Scraping failed: {e.message}")
except TimeoutError:
    print("Request timed out")
```

### Check Usage & Balance

```python
usage = client.get_usage()
print(f"Balance: ${usage.balance_dollars:.2f}")
print(f"Used this month: {usage.credits_used_month} credits")
```

## API Reference

### AlterLab Client

```python
AlterLab(
    api_key: str = None,           # API key (or ALTERLAB_API_KEY env var)
    base_url: str = None,          # Custom API URL
    timeout: int = 120,            # Request timeout in seconds
    max_retries: int = 3,          # Retry count for transient failures
    retry_delay: float = 1.0       # Initial retry delay (exponential backoff)
)
```

### scrape() Method

```python
client.scrape(
    url: str,                      # URL to scrape
    mode: str = "auto",            # "auto", "html", "js", "pdf", "ocr"
    sync: bool = True,             # Wait for result vs return job ID
    advanced: AdvancedOptions,     # Advanced scraping options
    cost_controls: CostControls,   # Budget and optimization settings
    cache: bool = False,           # Enable response caching
    cache_ttl: int = None,         # Cache TTL in seconds (60-86400)
    formats: list = None,          # Output formats: ["text", "json", "html", "markdown"]
    extraction_schema: dict,       # JSON Schema for structured extraction
    extraction_prompt: str,        # Natural language extraction instructions
    extraction_profile: str,       # Pre-built profile: "product", "article", etc.
    wait_for: str = None,          # CSS selector to wait for (JS mode)
    screenshot: bool = False,      # Capture screenshot (JS mode)
) -> ScrapeResult
```

### ScrapeResult

```python
result.url                # Scraped URL
result.status_code        # HTTP status
result.text               # Extracted text content
result.html               # HTML content
result.json               # Structured JSON content
result.title              # Page title
result.author             # Author (if detected)
result.billing            # BillingDetails object
result.billing.tier_used  # Tier that succeeded
result.billing.cost_dollars  # Final cost in USD
result.screenshot_url     # Screenshot URL (if requested)
result.pdf_url            # PDF URL (if requested)
result.cached             # Whether result was from cache
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ALTERLAB_API_KEY` | Your API key (alternative to passing in constructor) |

## Requirements

- Python 3.8+
- httpx >= 0.24.0

## Support

- **Documentation**: [https://alterlab.io/docs](https://alterlab.io/docs)
- **API Status**: [https://status.alterlab.io](https://status.alterlab.io)
- **Support**: support@alterlab.io
- **Issues**: [GitHub Issues](https://github.com/RapierCraft/AlterLab-SDK/issues)

## License

MIT License - see [LICENSE](LICENSE) for details.
