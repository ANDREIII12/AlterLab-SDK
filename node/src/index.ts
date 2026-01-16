/**
 * AlterLab Node.js SDK - Official client for the AlterLab Web Scraping API.
 *
 * @example
 * ```typescript
 * import { AlterLab } from 'alterlab';
 *
 * const client = new AlterLab({ apiKey: 'sk_live_...' });
 * const result = await client.scrape('https://example.com');
 * console.log(result.text);
 * ```
 *
 * @packageDocumentation
 */

export const VERSION = '2.0.0';

// ============================================================================
// Types & Interfaces
// ============================================================================

/** Scraping mode */
export type ScrapeMode = 'auto' | 'html' | 'js' | 'pdf' | 'ocr';

/** Output format options */
export type OutputFormat = 'text' | 'json' | 'html' | 'markdown';

/** Tier names */
export type TierName = 'curl' | 'http' | 'stealth' | 'browser' | 'captcha';

/** Cost preference */
export type CostPreference = 'cost' | 'speed' | 'balanced';

/** Wait condition for JS rendering */
export type WaitCondition = 'load' | 'domcontentloaded' | 'networkidle';

/** Job status */
export type JobStatusType = 'pending' | 'processing' | 'completed' | 'failed';

/**
 * Advanced scraping options
 */
export interface AdvancedOptions {
  /** Enable JavaScript rendering */
  renderJs?: boolean;
  /** Capture screenshot */
  screenshot?: boolean;
  /** Generate PDF */
  generatePdf?: boolean;
  /** Convert to markdown */
  markdown?: boolean;
  /** Wait condition for JS rendering */
  waitCondition?: WaitCondition;
  /** Custom wait time in ms */
  waitTime?: number;
  /** CSS selector to wait for */
  waitForSelector?: string;
  /** Use your own proxy (20% discount) */
  useOwnProxy?: boolean;
  /** Proxy country code */
  proxyCountry?: string;
  /** Custom headers */
  headers?: Record<string, string>;
  /** Custom cookies */
  cookies?: string;
  /** Block resources (images, css, etc.) */
  blockResources?: string[];
  /** Viewport width */
  viewportWidth?: number;
  /** Viewport height */
  viewportHeight?: number;
  /** Mobile emulation */
  mobile?: boolean;
}

/**
 * Cost control settings
 */
export interface CostControls {
  /** Maximum tier to use (1-5 or tier name) */
  maxTier?: number | TierName;
  /** Optimize for cost vs speed */
  prefer?: CostPreference;
  /** Fail instead of escalating tiers */
  failFast?: boolean;
  /** Maximum cost in dollars */
  maxCostDollars?: number;
}

/**
 * Tier escalation details
 */
export interface TierEscalation {
  /** Tier number */
  tier: number;
  /** Tier name */
  name: TierName;
  /** Whether this tier succeeded */
  success: boolean;
  /** Error message if failed */
  error?: string;
  /** Time spent on this tier in ms */
  durationMs: number;
}

/**
 * Billing details for a scrape
 */
export interface BillingDetails {
  /** Tier that succeeded (1-5) */
  tierUsed: number;
  /** Tier name */
  tierName: TierName;
  /** Cost in microcents (1,000,000 = $1) */
  costMicrocents: number;
  /** Cost in dollars */
  costDollars: number;
  /** Whether BYOP discount was applied */
  byopApplied: boolean;
  /** BYOP discount percentage */
  byopDiscountPercent: number;
  /** Tier escalation history */
  escalationPath: TierEscalation[];
}

/**
 * Scrape result
 */
export interface ScrapeResult {
  /** Request ID */
  requestId: string;
  /** Scraped URL */
  url: string;
  /** Final URL after redirects */
  finalUrl: string;
  /** HTTP status code */
  statusCode: number;
  /** Extracted text content */
  text: string;
  /** Raw HTML content */
  html: string;
  /** Structured JSON content */
  json: Record<string, unknown> | null;
  /** Markdown content (if requested) */
  markdownContent: string | null;
  /** Page title */
  title: string | null;
  /** Page description */
  description: string | null;
  /** Author (if detected) */
  author: string | null;
  /** Published date (if detected) */
  publishedDate: string | null;
  /** Screenshot URL (if requested) */
  screenshotUrl: string | null;
  /** PDF URL (if requested) */
  pdfUrl: string | null;
  /** Whether result was from cache */
  cached: boolean;
  /** Response time in ms */
  responseTimeMs: number;
  /** Content size in bytes */
  sizeBytes: number;
  /** Billing details */
  billing: BillingDetails;
}

/**
 * Cost estimate result
 */
export interface CostEstimate {
  /** Estimated tier */
  estimatedTier: number;
  /** Tier name */
  tierName: TierName;
  /** Estimated cost in dollars */
  estimatedCostDollars: number;
  /** Min cost (if escalation needed) */
  minCostDollars: number;
  /** Max cost (if escalation needed) */
  maxCostDollars: number;
  /** Confidence level */
  confidence: 'high' | 'medium' | 'low';
  /** Reason for estimate */
  reason: string;
}

/**
 * Usage statistics
 */
export interface UsageStats {
  /** Current balance in dollars */
  balanceDollars: number;
  /** Credits used this month */
  creditsUsedMonth: number;
  /** Total requests this month */
  requestsMonth: number;
  /** Billing period start */
  periodStart: string;
  /** Billing period end */
  periodEnd: string;
}

/**
 * Job status for async scraping
 */
export interface JobStatus {
  /** Job ID */
  jobId: string;
  /** Current status */
  status: JobStatusType;
  /** Progress percentage (0-100) */
  progress: number;
  /** Result if completed */
  result?: ScrapeResult;
  /** Error message if failed */
  error?: string;
  /** Created timestamp */
  createdAt: string;
  /** Updated timestamp */
  updatedAt: string;
}

/**
 * Scrape request options
 */
export interface ScrapeOptions {
  /** Scraping mode */
  mode?: ScrapeMode;
  /** Wait for result (sync) or return job ID (async) */
  sync?: boolean;
  /** Advanced options */
  advanced?: AdvancedOptions;
  /** Cost controls */
  costControls?: CostControls;
  /** Enable caching */
  cache?: boolean;
  /** Cache TTL in seconds */
  cacheTtl?: number;
  /** Force cache refresh */
  forceRefresh?: boolean;
  /** Output formats to include */
  formats?: OutputFormat[];
  /** JSON Schema for structured extraction */
  extractionSchema?: Record<string, unknown>;
  /** Natural language extraction prompt */
  extractionPrompt?: string;
  /** Pre-built extraction profile */
  extractionProfile?: string;
  /** CSS selector to wait for */
  waitFor?: string;
  /** Capture screenshot */
  screenshot?: boolean;
  /** Request timeout in ms */
  timeout?: number;
}

/**
 * Client configuration
 */
export interface AlterLabConfig {
  /** API key */
  apiKey?: string;
  /** Base URL for API */
  baseUrl?: string;
  /** Request timeout in ms */
  timeout?: number;
  /** Max retries for transient failures */
  maxRetries?: number;
  /** Initial retry delay in ms */
  retryDelay?: number;
}

// ============================================================================
// Errors
// ============================================================================

/**
 * Base error for all AlterLab errors
 */
export class AlterLabError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'AlterLabError';
  }
}

/**
 * API error with status code and details
 */
export class AlterLabAPIError extends AlterLabError {
  constructor(
    message: string,
    public statusCode: number,
    public code?: string,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'AlterLabAPIError';
  }
}

/**
 * Authentication error (invalid API key)
 */
export class AuthenticationError extends AlterLabAPIError {
  constructor(message = 'Invalid or missing API key') {
    super(message, 401, 'AUTHENTICATION_ERROR');
    this.name = 'AuthenticationError';
  }
}

/**
 * Insufficient credits error
 */
export class InsufficientCreditsError extends AlterLabAPIError {
  constructor(
    message = 'Insufficient credits',
    public balanceDollars?: number,
    public requiredDollars?: number
  ) {
    super(message, 402, 'INSUFFICIENT_CREDITS', { balanceDollars, requiredDollars });
    this.name = 'InsufficientCreditsError';
  }
}

/**
 * Rate limit error
 */
export class RateLimitError extends AlterLabAPIError {
  constructor(
    message = 'Rate limit exceeded',
    public retryAfter?: number
  ) {
    super(message, 429, 'RATE_LIMIT_EXCEEDED', { retryAfter });
    this.name = 'RateLimitError';
  }
}

/**
 * Validation error
 */
export class ValidationError extends AlterLabAPIError {
  constructor(
    message: string,
    public field?: string
  ) {
    super(message, 400, 'VALIDATION_ERROR', { field });
    this.name = 'ValidationError';
  }
}

/**
 * Scrape error
 */
export class ScrapeError extends AlterLabAPIError {
  constructor(
    message: string,
    public url?: string,
    public tier?: number
  ) {
    super(message, 422, 'SCRAPE_ERROR', { url, tier });
    this.name = 'ScrapeError';
  }
}

/**
 * Timeout error
 */
export class TimeoutError extends AlterLabError {
  constructor(message = 'Request timed out') {
    super(message);
    this.name = 'TimeoutError';
  }
}

// ============================================================================
// Utility Functions
// ============================================================================

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function toSnakeCase(str: string): string {
  return str.replace(/[A-Z]/g, (letter) => `_${letter.toLowerCase()}`);
}

function toSnakeCaseKeys(obj: Record<string, unknown>): Record<string, unknown> {
  const result: Record<string, unknown> = {};
  for (const [key, value] of Object.entries(obj)) {
    const snakeKey = toSnakeCase(key);
    if (value && typeof value === 'object' && !Array.isArray(value)) {
      result[snakeKey] = toSnakeCaseKeys(value as Record<string, unknown>);
    } else {
      result[snakeKey] = value;
    }
  }
  return result;
}

function toCamelCase(str: string): string {
  return str.replace(/_([a-z])/g, (_, letter: string) => letter.toUpperCase());
}

function toCamelCaseKeys<T>(obj: unknown): T {
  if (Array.isArray(obj)) {
    return obj.map((item) => toCamelCaseKeys(item)) as T;
  }
  if (obj && typeof obj === 'object') {
    const result: Record<string, unknown> = {};
    for (const [key, value] of Object.entries(obj)) {
      const camelKey = toCamelCase(key);
      result[camelKey] = toCamelCaseKeys(value);
    }
    return result as T;
  }
  return obj as T;
}

// ============================================================================
// HTTP Client
// ============================================================================

interface RequestOptions {
  method: 'GET' | 'POST' | 'PUT' | 'DELETE';
  path: string;
  body?: Record<string, unknown>;
  timeout?: number;
}

async function makeRequest<T>(
  config: Required<AlterLabConfig>,
  options: RequestOptions
): Promise<T> {
  const url = `${config.baseUrl}${options.path}`;
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), options.timeout || config.timeout);

  try {
    const response = await fetch(url, {
      method: options.method,
      headers: {
        'Content-Type': 'application/json',
        'X-API-Key': config.apiKey,
        'User-Agent': `alterlab-node/${VERSION}`,
      },
      body: options.body ? JSON.stringify(toSnakeCaseKeys(options.body)) : undefined,
      signal: controller.signal,
    });

    clearTimeout(timeoutId);

    const data = (await response.json().catch(() => ({}))) as Record<string, unknown>;

    if (!response.ok) {
      throw handleAPIError(response.status, data);
    }

    return toCamelCaseKeys<T>(data);
  } catch (error) {
    clearTimeout(timeoutId);

    if (error instanceof AlterLabError) {
      throw error;
    }

    if (error instanceof Error) {
      if (error.name === 'AbortError') {
        throw new TimeoutError(`Request timed out after ${config.timeout}ms`);
      }
      throw new AlterLabError(`Request failed: ${error.message}`);
    }

    throw new AlterLabError('Unknown error occurred');
  }
}

function handleAPIError(status: number, data: Record<string, unknown>): AlterLabAPIError {
  const message = (data.detail as string) || (data.message as string) || 'API error';
  const code = data.code as string | undefined;

  switch (status) {
    case 401:
      return new AuthenticationError(message);
    case 402:
      return new InsufficientCreditsError(
        message,
        data.balance_dollars as number | undefined,
        data.required_dollars as number | undefined
      );
    case 429:
      return new RateLimitError(message, data.retry_after as number | undefined);
    case 400:
      return new ValidationError(message, data.field as string | undefined);
    case 422:
      return new ScrapeError(message, data.url as string | undefined, data.tier as number | undefined);
    default:
      return new AlterLabAPIError(message, status, code, data);
  }
}

async function requestWithRetry<T>(
  config: Required<AlterLabConfig>,
  options: RequestOptions
): Promise<T> {
  let lastError: Error | null = null;
  let delay = config.retryDelay;

  for (let attempt = 0; attempt <= config.maxRetries; attempt++) {
    try {
      return await makeRequest<T>(config, options);
    } catch (error) {
      lastError = error as Error;

      // Don't retry on client errors (except rate limits)
      if (error instanceof AlterLabAPIError) {
        if (error.statusCode >= 400 && error.statusCode < 500 && error.statusCode !== 429) {
          throw error;
        }
        // For rate limits, use retry-after if provided
        if (error instanceof RateLimitError && error.retryAfter) {
          delay = error.retryAfter * 1000;
        }
      }

      if (attempt < config.maxRetries) {
        await sleep(delay);
        delay *= 2; // Exponential backoff
      }
    }
  }

  throw lastError;
}

// ============================================================================
// AlterLab Client
// ============================================================================

/**
 * AlterLab API client for web scraping.
 *
 * @example
 * ```typescript
 * const client = new AlterLab({ apiKey: 'sk_live_...' });
 *
 * // Simple scrape
 * const result = await client.scrape('https://example.com');
 * console.log(result.text);
 *
 * // With options
 * const result = await client.scrape('https://spa-app.com', {
 *   mode: 'js',
 *   screenshot: true,
 *   costControls: { maxTier: 3 }
 * });
 * ```
 */
export class AlterLab {
  private config: Required<AlterLabConfig>;

  constructor(options: AlterLabConfig = {}) {
    const apiKey = options.apiKey || process.env.ALTERLAB_API_KEY;
    if (!apiKey) {
      throw new AuthenticationError(
        'API key is required. Pass it to the constructor or set ALTERLAB_API_KEY environment variable.'
      );
    }

    this.config = {
      apiKey,
      baseUrl: options.baseUrl || 'https://alterlab.io',
      timeout: options.timeout || 120000,
      maxRetries: options.maxRetries ?? 3,
      retryDelay: options.retryDelay || 1000,
    };
  }

  /**
   * Scrape a URL with automatic mode detection and tier escalation.
   */
  async scrape(url: string, options: ScrapeOptions = {}): Promise<ScrapeResult> {
    const body: Record<string, unknown> = {
      url,
      mode: options.mode || 'auto',
      sync: options.sync !== false,
    };

    if (options.advanced) {
      Object.assign(body, options.advanced);
    }

    if (options.costControls) {
      body.costControls = options.costControls;
    }

    if (options.cache !== undefined) body.cache = options.cache;
    if (options.cacheTtl !== undefined) body.cacheTtl = options.cacheTtl;
    if (options.forceRefresh !== undefined) body.forceRefresh = options.forceRefresh;
    if (options.formats) body.formats = options.formats;
    if (options.extractionSchema) body.extractionSchema = options.extractionSchema;
    if (options.extractionPrompt) body.extractionPrompt = options.extractionPrompt;
    if (options.extractionProfile) body.extractionProfile = options.extractionProfile;
    if (options.waitFor) body.waitFor = options.waitFor;
    if (options.screenshot) body.screenshot = options.screenshot;

    const response = await requestWithRetry<ScrapeResult>(this.config, {
      method: 'POST',
      path: '/api/v1/scrape',
      body,
      timeout: options.timeout,
    });

    return response;
  }

  /**
   * Scrape with HTML-only mode (fastest, cheapest).
   */
  async scrapeHtml(url: string, options: Omit<ScrapeOptions, 'mode'> = {}): Promise<ScrapeResult> {
    return this.scrape(url, { ...options, mode: 'html' });
  }

  /**
   * Scrape with JavaScript rendering.
   */
  async scrapeJs(url: string, options: Omit<ScrapeOptions, 'mode'> = {}): Promise<ScrapeResult> {
    return this.scrape(url, { ...options, mode: 'js' });
  }

  /**
   * Extract text from a PDF URL.
   */
  async scrapePdf(
    url: string,
    options: { format?: 'text' | 'markdown'; timeout?: number } = {}
  ): Promise<ScrapeResult> {
    return this.scrape(url, { mode: 'pdf', timeout: options.timeout });
  }

  /**
   * Extract text from an image using OCR.
   */
  async scrapeOcr(
    url: string,
    options: { language?: string; timeout?: number } = {}
  ): Promise<ScrapeResult> {
    const body: Record<string, unknown> = { url, mode: 'ocr' };
    if (options.language) body.language = options.language;

    return requestWithRetry<ScrapeResult>(this.config, {
      method: 'POST',
      path: '/api/v1/scrape',
      body,
      timeout: options.timeout,
    });
  }

  /**
   * Estimate the cost of scraping a URL.
   */
  async estimateCost(url: string): Promise<CostEstimate> {
    return requestWithRetry<CostEstimate>(this.config, {
      method: 'POST',
      path: '/api/v1/scrape/estimate',
      body: { url },
    });
  }

  /**
   * Get account usage statistics.
   */
  async getUsage(): Promise<UsageStats> {
    return requestWithRetry<UsageStats>(this.config, {
      method: 'GET',
      path: '/api/v1/usage',
    });
  }

  /**
   * Get the status of an async scrape job.
   */
  async getJobStatus(jobId: string): Promise<JobStatus> {
    return requestWithRetry<JobStatus>(this.config, {
      method: 'GET',
      path: `/api/v1/jobs/${jobId}`,
    });
  }

  /**
   * Wait for an async job to complete.
   */
  async waitForJob(
    jobId: string,
    options: { pollInterval?: number; timeout?: number } = {}
  ): Promise<ScrapeResult> {
    const pollInterval = options.pollInterval || 2000;
    const timeout = options.timeout || 300000;
    const startTime = Date.now();

    while (Date.now() - startTime < timeout) {
      const status = await this.getJobStatus(jobId);

      if (status.status === 'completed' && status.result) {
        return status.result;
      }

      if (status.status === 'failed') {
        throw new ScrapeError(status.error || 'Job failed');
      }

      await sleep(pollInterval);
    }

    throw new TimeoutError(`Job ${jobId} did not complete within ${timeout}ms`);
  }

  /**
   * Start an async scrape job.
   */
  async scrapeAsync(url: string, options: Omit<ScrapeOptions, 'sync'> = {}): Promise<string> {
    const body: Record<string, unknown> = {
      url,
      mode: options.mode || 'auto',
      sync: false,
    };

    if (options.advanced) Object.assign(body, options.advanced);
    if (options.costControls) body.costControls = options.costControls;
    if (options.extractionSchema) body.extractionSchema = options.extractionSchema;
    if (options.extractionPrompt) body.extractionPrompt = options.extractionPrompt;
    if (options.extractionProfile) body.extractionProfile = options.extractionProfile;

    const response = await requestWithRetry<{ jobId: string }>(this.config, {
      method: 'POST',
      path: '/api/v1/scrape',
      body,
    });

    return response.jobId;
  }
}

// ============================================================================
// Default Export
// ============================================================================

export default AlterLab;
