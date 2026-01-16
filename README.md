# AlterLab SDKs

Official SDKs for the [AlterLab Web Scraping API](https://alterlab.io). Extract data from any website with intelligent anti-bot bypass, JavaScript rendering, and structured extraction.

## Available SDKs

| Language | Package | Install | Status |
|----------|---------|---------|--------|
| **Python** | [alterlab](https://pypi.org/project/alterlab/) | `pip install alterlab` | [![PyPI](https://badge.fury.io/py/alterlab.svg)](https://pypi.org/project/alterlab/) |
| **Node.js** | [alterlab](https://www.npmjs.com/package/alterlab) | `npm install alterlab` | [![npm](https://badge.fury.io/js/alterlab.svg)](https://www.npmjs.com/package/alterlab) |

## Quick Start

### Python

```python
from alterlab import AlterLab

client = AlterLab(api_key="sk_live_...")
result = client.scrape("https://example.com")
print(result.text)
print(f"Cost: ${result.billing.cost_dollars}")
```

### Node.js / TypeScript

```typescript
import { AlterLab } from 'alterlab';

const client = new AlterLab({ apiKey: 'sk_live_...' });
const result = await client.scrape('https://example.com');
console.log(result.text);
console.log(`Cost: $${result.billing.costDollars}`);
```

## Features

- **Simple API**: 3 lines of code to scrape any website
- **Intelligent Anti-Bot Bypass**: Automatic tier escalation (curl → HTTP → stealth → browser)
- **JavaScript Rendering**: Full Playwright browser for JS-heavy sites
- **Structured Extraction**: JSON Schema, prompts, and pre-built profiles
- **BYOP Support**: Bring Your Own Proxy for 20% discount
- **Cost Controls**: Set budgets, prefer cost/speed, fail-fast options

## Pricing

Pay-as-you-go pricing with no subscriptions. **$1 = 5,000 scrapes** (Tier 1).

| Tier | Name | Price | Per $1 | Use Case |
|------|------|-------|--------|----------|
| 1 | Curl | $0.0002 | 5,000 | Static HTML sites |
| 2 | HTTP | $0.0003 | 3,333 | Sites with TLS fingerprinting |
| 3 | Stealth | $0.0005 | 2,000 | Sites with browser checks |
| 4 | Browser | $0.001 | 1,000 | JS-heavy SPAs |
| 5 | Captcha | $0.02 | 50 | Sites with CAPTCHAs |

## Documentation

- **Full Documentation**: [https://alterlab.io/docs](https://alterlab.io/docs)
- **Python SDK**: [python/README.md](python/README.md)
- **Node.js SDK**: [node/README.md](node/README.md)

## Support

- **API Status**: [https://status.alterlab.io](https://status.alterlab.io)
- **Email**: support@alterlab.io
- **Issues**: [GitHub Issues](https://github.com/RapierCraft/AlterLab-SDK/issues)

## License

MIT License - see individual SDK directories for details.
