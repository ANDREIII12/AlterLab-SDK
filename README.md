<p align="center">
  <img src="https://alterlab.io/logo.png" alt="AlterLab" width="200" />
</p>

<h1 align="center">AlterLab SDKs</h1>

<p align="center">
  <strong>Scrape any website. No blocks. No hassle.</strong>
</p>

<p align="center">
  Official SDKs for the <a href="https://alterlab.io">AlterLab Web Scraping API</a>
</p>

<p align="center">
  <a href="https://pypi.org/project/alterlab/"><img src="https://img.shields.io/pypi/v/alterlab?style=for-the-badge&logo=python&logoColor=white&label=PyPI&color=3776AB" alt="PyPI version" /></a>
  <a href="https://www.npmjs.com/package/alterlab"><img src="https://img.shields.io/npm/v/alterlab?style=for-the-badge&logo=npm&logoColor=white&label=npm&color=CB3837" alt="npm version" /></a>
  <a href="https://github.com/RapierCraft/AlterLab-SDK/stargazers"><img src="https://img.shields.io/github/stars/RapierCraft/AlterLab-SDK?style=for-the-badge&logo=github&color=yellow" alt="GitHub stars" /></a>
  <a href="https://github.com/RapierCraft/AlterLab-SDK/blob/main/LICENSE"><img src="https://img.shields.io/github/license/RapierCraft/AlterLab-SDK?style=for-the-badge&color=blue" alt="License" /></a>
</p>

<p align="center">
  <a href="https://alterlab.io/docs/sdk">Documentation</a> •
  <a href="https://alterlab.io/docs/sdk/python">Python Docs</a> •
  <a href="https://alterlab.io/docs/sdk/node">Node.js Docs</a> •
  <a href="https://alterlab.io/playground">Playground</a>
</p>

---

## Why AlterLab?

- **🚀 3 Lines of Code** — Scrape any website in seconds
- **🛡️ Anti-Bot Bypass** — Automatic escalation through 5 tiers (curl → HTTP → stealth → browser → captcha)
- **⚡ Blazing Fast** — Average response time under 2 seconds for static sites
- **💰 Pay-As-You-Go** — No subscriptions. **$1 = 5,000 scrapes**. Credits never expire.
- **🔧 Zero Config** — Works out of the box. No proxies to manage.

## Quick Install

```bash
# Python
pip install alterlab

# Node.js
npm install alterlab
```

## Quick Start

### Python

```python
from alterlab import AlterLab

client = AlterLab(api_key="sk_live_...")
result = client.scrape("https://example.com")

print(result.text)                    # Extracted text
print(result.json)                    # Structured data
print(f"Cost: ${result.billing.cost_dollars}")  # $0.0002
```

### Node.js / TypeScript

```typescript
import { AlterLab } from 'alterlab';

const client = new AlterLab({ apiKey: 'sk_live_...' });
const result = await client.scrape('https://example.com');

console.log(result.text);                    // Extracted text
console.log(result.json);                    // Structured data
console.log(`Cost: $${result.billing.costDollars}`);  // $0.0002
```

## Features

| Feature | Description |
|---------|-------------|
| **🎯 Intelligent Scraping** | Auto-selects the best approach for each site |
| **🌐 JavaScript Rendering** | Full Playwright browser for SPAs and dynamic content |
| **📊 Structured Extraction** | JSON Schema, AI prompts, or pre-built profiles (product, article, etc.) |
| **🔐 BYOP Support** | Bring Your Own Proxy for 20% discount |
| **💸 Cost Controls** | Set max tier, budget limits, prefer cost vs speed |
| **⚡ Async Support** | Native async/await for concurrent scraping |
| **📝 Full TypeScript** | Complete type definitions for excellent DX |
| **🔄 Auto Retries** | Exponential backoff with configurable retry logic |
| **📸 Screenshots & PDFs** | Capture visual snapshots of any page |
| **🔍 OCR** | Extract text from images |

## Pricing

**$1 = 5,000 scrapes** (Tier 1) — The API automatically escalates through tiers until successful.

| Tier | Name | Price | Per $1 | Best For |
|:----:|------|------:|-------:|----------|
| 1 | Curl | $0.0002 | 5,000 | Static HTML, blogs, docs |
| 2 | HTTP | $0.0003 | 3,333 | Sites with TLS fingerprinting |
| 3 | Stealth | $0.0005 | 2,000 | Cloudflare, DataDome |
| 4 | Browser | $0.001 | 1,000 | React/Vue SPAs, infinite scroll |
| 5 | Captcha | $0.02 | 50 | hCaptcha, reCAPTCHA |

**No subscriptions. No monthly fees. Credits never expire.**

<details>
<summary><strong>🎁 Free Tier</strong></summary>

Get **5,000 free scrapes** when you sign up — no credit card required.

[Get Started Free →](https://alterlab.io/signup)

</details>

## Advanced Examples

<details>
<summary><strong>Structured Extraction with JSON Schema</strong></summary>

```python
result = client.scrape(
    "https://amazon.com/dp/B08N5WRWNW",
    extraction_schema={
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "price": {"type": "number"},
            "rating": {"type": "number"},
            "reviews_count": {"type": "integer"}
        }
    }
)
print(result.json)
# {"title": "Product Name", "price": 29.99, "rating": 4.5, "reviews_count": 1234}
```

</details>

<details>
<summary><strong>JavaScript Rendering with Screenshot</strong></summary>

```python
result = client.scrape_js(
    "https://spa-app.com",
    screenshot=True,
    wait_for="#main-content"
)
print(result.screenshot_url)  # URL to screenshot image
```

</details>

<details>
<summary><strong>Cost Controls</strong></summary>

```python
from alterlab import AlterLab, CostControls

result = client.scrape(
    "https://example.com",
    cost_controls=CostControls(
        max_tier="2",       # Never use browser/captcha tiers
        prefer_cost=True,   # Optimize for lowest cost
        fail_fast=True      # Error instead of escalating
    )
)
```

</details>

<details>
<summary><strong>Async Concurrent Scraping</strong></summary>

```python
import asyncio
from alterlab import AsyncAlterLab

async def main():
    async with AsyncAlterLab(api_key="sk_live_...") as client:
        urls = ["https://example.com/1", "https://example.com/2", "https://example.com/3"]
        results = await asyncio.gather(*[client.scrape(url) for url in urls])

        for r in results:
            print(f"{r.url}: ${r.billing.cost_dollars}")

asyncio.run(main())
```

</details>

<details>
<summary><strong>BYOP (Bring Your Own Proxy)</strong></summary>

```python
from alterlab import AlterLab, AdvancedOptions

result = client.scrape(
    "https://example.com",
    advanced=AdvancedOptions(
        use_own_proxy=True,
        proxy_country="US"
    )
)

if result.billing.byop_applied:
    print("Saved 20%!")
```

</details>

## SDK Reference

| Language | Package | Version | Docs |
|----------|---------|---------|------|
| **Python** | [`alterlab`](https://pypi.org/project/alterlab/) | ![PyPI](https://img.shields.io/pypi/v/alterlab?style=flat-square) | [Python Docs](https://alterlab.io/docs/sdk/python) |
| **Node.js** | [`alterlab`](https://www.npmjs.com/package/alterlab) | ![npm](https://img.shields.io/npm/v/alterlab?style=flat-square) | [Node.js Docs](https://alterlab.io/docs/sdk/node) |

## Requirements

| SDK | Requirements |
|-----|--------------|
| Python | Python 3.8+ |
| Node.js | Node.js 18+ (uses native fetch) |

## Support

- 📚 **Documentation**: [alterlab.io/docs](https://alterlab.io/docs)
- 🎮 **Playground**: [alterlab.io/playground](https://alterlab.io/playground)
- 📊 **API Status**: [status.alterlab.io](https://status.alterlab.io)
- 💬 **Discord**: [Join our community](https://discord.gg/alterlab)
- 📧 **Email**: support@alterlab.io
- 🐛 **Issues**: [GitHub Issues](https://github.com/RapierCraft/AlterLab-SDK/issues)

## Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT License — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <a href="https://alterlab.io">Website</a> •
  <a href="https://alterlab.io/docs">Docs</a> •
  <a href="https://twitter.com/alterlabio">Twitter</a> •
  <a href="https://discord.gg/alterlab">Discord</a>
</p>

<p align="center">
  <sub>Built with ❤️ by the AlterLab team</sub>
</p>
