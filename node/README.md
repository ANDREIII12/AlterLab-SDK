# AlterLab Node.js SDK

Official Node.js/TypeScript SDK for the [AlterLab Web Scraping API](https://alterlab.io). Extract data from any website with intelligent anti-bot bypass, JavaScript rendering, and structured extraction.

[![npm version](https://badge.fury.io/js/alterlab.svg)](https://badge.fury.io/js/alterlab)
[![Node.js 18+](https://img.shields.io/badge/node-18+-green.svg)](https://nodejs.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-Ready-blue.svg)](https://www.typescriptlang.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Features

- **Simple API**: 3 lines of code to scrape any website
- **Intelligent Anti-Bot Bypass**: Automatic tier escalation (curl → HTTP → stealth → browser)
- **JavaScript Rendering**: Full Playwright browser for JS-heavy sites
- **Structured Extraction**: JSON Schema, prompts, and pre-built profiles
- **BYOP Support**: Bring Your Own Proxy for 20% discount
- **Full TypeScript**: Complete type definitions for IDE autocomplete
- **Cost Controls**: Set budgets, prefer cost/speed, fail-fast options
- **Zero Dependencies**: Uses native fetch (Node.js 18+)

## Installation

```bash
npm install alterlab
# or
yarn add alterlab
# or
pnpm add alterlab
```

## Quick Start

```typescript
import { AlterLab } from 'alterlab';

// Initialize client
const client = new AlterLab({ apiKey: 'sk_live_...' }); // or set ALTERLAB_API_KEY env var

// Scrape a website
const result = await client.scrape('https://example.com');
console.log(result.text);           // Extracted text
console.log(result.json);           // Structured JSON (Schema.org, metadata)
console.log(result.billing.costDollars); // Cost breakdown
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

```typescript
import { AlterLab } from 'alterlab';

const client = new AlterLab({ apiKey: 'sk_live_...' });

// Auto mode - intelligent tier escalation
const result = await client.scrape('https://example.com');

// Force HTML-only (fastest, cheapest)
const htmlResult = await client.scrapeHtml('https://example.com');

// JavaScript rendering
const jsResult = await client.scrapeJs('https://spa-app.com', { screenshot: true });
console.log(jsResult.screenshotUrl);
```

### Structured Extraction

```typescript
// Extract specific fields with JSON Schema
const result = await client.scrape('https://store.com/product/123', {
  extractionSchema: {
    type: 'object',
    properties: {
      name: { type: 'string' },
      price: { type: 'number' },
      inStock: { type: 'boolean' }
    }
  }
});
console.log(result.json); // { name: "...", price: 29.99, inStock: true }

// Or use a pre-built profile
const productResult = await client.scrape('https://store.com/product/123', {
  extractionProfile: 'product'
});
```

### Cost Controls

```typescript
import { AlterLab, CostControls } from 'alterlab';

const client = new AlterLab({ apiKey: 'sk_live_...' });

// Limit to cheap tiers only
const result = await client.scrape('https://example.com', {
  costControls: {
    maxTier: 2,        // Don't go above HTTP tier
    prefer: 'cost',    // Optimize for lowest cost
    failFast: true     // Error instead of escalating
  }
});

// Estimate cost before scraping
const estimate = await client.estimateCost('https://linkedin.com');
console.log(`Estimated: $${estimate.estimatedCostDollars.toFixed(4)}`);
console.log(`Confidence: ${estimate.confidence}`);
```

### Advanced Options

```typescript
import { AlterLab } from 'alterlab';

const client = new AlterLab({ apiKey: 'sk_live_...' });

// Full browser with screenshot and PDF
const result = await client.scrape('https://example.com', {
  mode: 'js',
  advanced: {
    renderJs: true,
    screenshot: true,
    generatePdf: true,
    markdown: true,
    waitCondition: 'networkidle'
  }
});

console.log(result.screenshotUrl);
console.log(result.pdfUrl);
console.log(result.markdownContent);
```

### BYOP (Bring Your Own Proxy)

Get 20% discount when using your own proxy:

```typescript
import { AlterLab } from 'alterlab';

const client = new AlterLab({ apiKey: 'sk_live_...' });

// Use your configured proxy integration
const result = await client.scrape('https://example.com', {
  advanced: {
    useOwnProxy: true,
    proxyCountry: 'US' // Optional: request specific geo
  }
});

// Check if BYOP was applied
if (result.billing.byopApplied) {
  console.log(`Saved ${result.billing.byopDiscountPercent}%!`);
}
```

### Async Jobs

```typescript
import { AlterLab } from 'alterlab';

const client = new AlterLab({ apiKey: 'sk_live_...' });

// Start an async job
const jobId = await client.scrapeAsync('https://example.com', {
  mode: 'js',
  advanced: { screenshot: true }
});

console.log(`Job started: ${jobId}`);

// Wait for completion
const result = await client.waitForJob(jobId, {
  pollInterval: 2000,  // Check every 2 seconds
  timeout: 300000      // 5 minute timeout
});

console.log(result.text);
```

### Caching

```typescript
// Enable caching (opt-in)
const result = await client.scrape('https://example.com', {
  cache: true,         // Enable caching
  cacheTtl: 3600       // Cache for 1 hour
});

if (result.cached) {
  console.log('Cache hit - no credits charged!');
}

// Force refresh
const freshResult = await client.scrape('https://example.com', {
  cache: true,
  forceRefresh: true   // Bypass cache
});
```

### Error Handling

```typescript
import {
  AlterLab,
  AuthenticationError,
  InsufficientCreditsError,
  RateLimitError,
  ScrapeError,
  TimeoutError
} from 'alterlab';

const client = new AlterLab({ apiKey: 'sk_live_...' });

try {
  const result = await client.scrape('https://example.com');
} catch (error) {
  if (error instanceof AuthenticationError) {
    console.log('Invalid API key');
  } else if (error instanceof InsufficientCreditsError) {
    console.log('Please top up your balance');
  } else if (error instanceof RateLimitError) {
    console.log(`Rate limited. Retry after ${error.retryAfter}s`);
  } else if (error instanceof ScrapeError) {
    console.log(`Scraping failed: ${error.message}`);
  } else if (error instanceof TimeoutError) {
    console.log('Request timed out');
  }
}
```

### Check Usage & Balance

```typescript
const usage = await client.getUsage();
console.log(`Balance: $${usage.balanceDollars.toFixed(2)}`);
console.log(`Used this month: ${usage.creditsUsedMonth} credits`);
```

## API Reference

### AlterLab Client

```typescript
new AlterLab({
  apiKey?: string,        // API key (or ALTERLAB_API_KEY env var)
  baseUrl?: string,       // Custom API URL
  timeout?: number,       // Request timeout in ms (default: 120000)
  maxRetries?: number,    // Retry count for transient failures (default: 3)
  retryDelay?: number     // Initial retry delay in ms (default: 1000)
})
```

### scrape() Method

```typescript
client.scrape(url: string, {
  mode?: 'auto' | 'html' | 'js' | 'pdf' | 'ocr',  // Scraping mode
  sync?: boolean,                  // Wait for result vs return job ID
  advanced?: AdvancedOptions,      // Advanced scraping options
  costControls?: CostControls,     // Budget and optimization settings
  cache?: boolean,                 // Enable response caching
  cacheTtl?: number,               // Cache TTL in seconds (60-86400)
  forceRefresh?: boolean,          // Bypass cache
  formats?: OutputFormat[],        // Output formats
  extractionSchema?: object,       // JSON Schema for structured extraction
  extractionPrompt?: string,       // Natural language extraction
  extractionProfile?: string,      // Pre-built profile
  waitFor?: string,                // CSS selector to wait for
  screenshot?: boolean,            // Capture screenshot
  timeout?: number                 // Request timeout in ms
}): Promise<ScrapeResult>
```

### ScrapeResult

```typescript
interface ScrapeResult {
  requestId: string;        // Unique request ID
  url: string;              // Scraped URL
  finalUrl: string;         // URL after redirects
  statusCode: number;       // HTTP status
  text: string;             // Extracted text content
  html: string;             // HTML content
  json: object | null;      // Structured JSON content
  markdownContent: string | null;  // Markdown (if requested)
  title: string | null;     // Page title
  author: string | null;    // Author (if detected)
  screenshotUrl: string | null;    // Screenshot URL
  pdfUrl: string | null;    // PDF URL
  cached: boolean;          // Whether from cache
  responseTimeMs: number;   // Response time
  sizeBytes: number;        // Content size
  billing: BillingDetails;  // Cost breakdown
}
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `ALTERLAB_API_KEY` | Your API key (alternative to constructor) |

## Requirements

- Node.js 18+ (uses native fetch)
- TypeScript 5.0+ (optional, for type definitions)

## Support

- **Documentation**: [https://alterlab.io/docs](https://alterlab.io/docs)
- **API Status**: [https://status.alterlab.io](https://status.alterlab.io)
- **Support**: support@alterlab.io
- **Issues**: [GitHub Issues](https://github.com/RapierCraft/AlterLab-SDK/issues)

## License

MIT License - see [LICENSE](LICENSE) for details.
