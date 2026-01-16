"""
AlterLab Python SDK - Official client for the AlterLab Web Scraping API.

Full feature parity with the AlterLab API including:
- Unified scraping endpoint with all modes (auto, html, js, pdf, ocr)
- Automatic job polling with exponential backoff
- Advanced options (render_js, screenshot, markdown, PDF generation, OCR)
- Cost controls (max_tier, prefer_cost/speed, fail_fast)
- Structured extraction (schemas, prompts, profiles)
- Cost estimation before scraping
- Usage tracking and credit management
- Batch scraping with webhooks
- BYOP (Bring Your Own Proxy) support
- Comprehensive error handling with retries

Pricing (Pay-as-you-go):
    Tier 1 (curl):    $0.0002/req - 5,000 per $1
    Tier 2 (http):    $0.0003/req - 3,333 per $1
    Tier 3 (stealth): $0.0005/req - 2,000 per $1
    Tier 4 (browser): $0.001/req  - 1,000 per $1
    Tier 5 (captcha): $0.02/req   - 50 per $1

Example:
    from alterlab import AlterLab

    client = AlterLab(api_key="sk_live_...")
    result = client.scrape("https://example.com")
    print(result.content)
"""

from __future__ import annotations

import asyncio
import os
import time
import warnings
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Union

try:
    import httpx
except ImportError:
    raise ImportError(
        "httpx is required for the AlterLab SDK. Install with: pip install httpx"
    )


__version__ = "2.0.0"


# =============================================================================
# EXCEPTIONS
# =============================================================================


class AlterLabError(Exception):
    """Base exception for all AlterLab SDK errors."""

    pass


class AlterLabAPIError(AlterLabError):
    """API returned an error response."""

    def __init__(
        self,
        status_code: int,
        message: str,
        response: Optional[httpx.Response] = None,
    ):
        self.status_code = status_code
        self.message = message
        self.response = response
        super().__init__(f"[{status_code}] {message}")


class AuthenticationError(AlterLabAPIError):
    """Invalid or missing API key (401)."""

    pass


class InsufficientCreditsError(AlterLabAPIError):
    """Insufficient balance to complete request (402)."""

    pass


class RateLimitError(AlterLabAPIError):
    """Rate limit exceeded (429)."""

    def __init__(
        self,
        message: str,
        retry_after: Optional[int] = None,
        response: Optional[httpx.Response] = None,
    ):
        super().__init__(429, message, response)
        self.retry_after = retry_after


class ValidationError(AlterLabAPIError):
    """Request validation failed (422)."""

    pass


class ScrapeError(AlterLabAPIError):
    """Scraping operation failed."""

    def __init__(
        self,
        status_code: int,
        message: str,
        code: Optional[str] = None,
        response: Optional[httpx.Response] = None,
    ):
        super().__init__(status_code, message, response)
        self.code = code


class TimeoutError(AlterLabError):
    """Request or job polling timed out."""

    pass


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class AdvancedOptions:
    """Advanced scraping options.

    Attributes:
        render_js: Render JavaScript using headless browser
        screenshot: Capture full-page screenshot (requires render_js)
        markdown: Extract content as Markdown
        generate_pdf: Generate PDF of rendered page (requires render_js)
        ocr: Extract text from images using OCR
        use_proxy: Route through premium proxy
        use_own_proxy: Use your integrated BYOP proxy (20% discount)
        use_system_proxy: Override BYOP and use AlterLab's proxy
        proxy_integration_id: Specific proxy integration ID (for BYOP)
        proxy_country: Preferred proxy country code (e.g., 'US', 'DE')
        wait_condition: Wait condition for JS rendering
        remove_cookie_banners: Remove cookie consent banners from HTML
    """

    render_js: bool = False
    screenshot: bool = False
    markdown: bool = False
    generate_pdf: bool = False
    ocr: bool = False
    use_proxy: bool = False
    use_own_proxy: bool = False
    use_system_proxy: bool = False
    proxy_integration_id: Optional[str] = None
    proxy_country: Optional[str] = None
    wait_condition: Literal["domcontentloaded", "networkidle", "load"] = "networkidle"
    remove_cookie_banners: bool = True

    def __post_init__(self):
        if self.screenshot and not self.render_js:
            raise ValueError("screenshot requires render_js=True")
        if self.generate_pdf and not self.render_js:
            raise ValueError("generate_pdf requires render_js=True")
        if self.wait_condition not in ("domcontentloaded", "networkidle", "load"):
            raise ValueError(
                "wait_condition must be 'domcontentloaded', 'networkidle', or 'load'"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API request format."""
        return {
            "render_js": self.render_js,
            "screenshot": self.screenshot,
            "markdown": self.markdown,
            "generate_pdf": self.generate_pdf,
            "ocr": self.ocr,
            "use_proxy": self.use_proxy,
            "use_own_proxy": self.use_own_proxy,
            "use_system_proxy": self.use_system_proxy,
            "proxy_integration_id": self.proxy_integration_id,
            "proxy_country": self.proxy_country,
            "wait_condition": self.wait_condition,
            "remove_cookie_banners": self.remove_cookie_banners,
        }


@dataclass
class CostControls:
    """Cost control parameters for scraping requests.

    Tier levels (1-5):
        1: curl    - Direct HTTP ($0.0002)
        2: http    - HTTPX with TLS fingerprinting ($0.0003)
        3: stealth - curl_cffi browser impersonation ($0.0005)
        4: browser - Playwright full rendering ($0.001)
        5: captcha - Browser + CAPTCHA solving ($0.02)

    Attributes:
        max_tier: Maximum tier to escalate to ("1"-"5")
        prefer_cost: Optimize for lowest cost (start at tier 1)
        prefer_speed: Optimize for speed (start at higher tier)
        fail_fast: Return error instead of escalating to expensive tiers
    """

    max_tier: Optional[Literal["1", "2", "3", "4", "5"]] = None
    prefer_cost: bool = False
    prefer_speed: bool = False
    fail_fast: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API request format."""
        result: Dict[str, Any] = {
            "prefer_cost": self.prefer_cost,
            "prefer_speed": self.prefer_speed,
            "fail_fast": self.fail_fast,
        }
        if self.max_tier:
            result["max_tier"] = self.max_tier
        return result


@dataclass
class TierEscalation:
    """Details of a tier escalation attempt."""

    tier: str
    result: Literal["success", "failed", "skipped"]
    credits: int
    duration_ms: Optional[int] = None
    error: Optional[str] = None


@dataclass
class BillingDetails:
    """Detailed billing information for a scrape request."""

    total_credits: int
    tier_used: str
    escalations: List[TierEscalation] = field(default_factory=list)
    savings: int = 0
    optimization_suggestion: Optional[str] = None
    byop_applied: bool = False
    byop_discount_percent: Optional[float] = None
    original_cost_microcents: Optional[int] = None
    final_cost_microcents: Optional[int] = None

    @property
    def cost_dollars(self) -> float:
        """Get the final cost in dollars."""
        if self.final_cost_microcents is not None:
            return self.final_cost_microcents / 1_000_000
        # Fallback to legacy credit calculation
        tier_costs = {"1": 0.0002, "2": 0.0003, "3": 0.0005, "4": 0.001, "5": 0.02}
        return tier_costs.get(self.tier_used, 0.0003)


@dataclass
class ScrapeResult:
    """Result from a scrape operation."""

    url: str
    status_code: int
    content: Union[str, Dict[str, Any]]
    title: Optional[str] = None
    author: Optional[str] = None
    published_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    headers: Dict[str, str] = field(default_factory=dict)
    cached: bool = False
    cached_at: Optional[str] = None
    expires_at: Optional[str] = None
    response_time_ms: int = 0
    size_bytes: int = 0
    raw_html: Optional[str] = None
    screenshot_url: Optional[str] = None
    pdf_url: Optional[str] = None
    ocr_results: Optional[List[Dict[str, Any]]] = None
    proxy_used: Optional[Dict[str, Any]] = None
    filtered_content: Optional[Dict[str, Any]] = None
    billing: Optional[BillingDetails] = None
    extraction_method: str = "algorithmic"
    method_details: Optional[Dict[str, Any]] = None

    @property
    def text(self) -> str:
        """Get text content."""
        if isinstance(self.content, dict):
            return self.content.get("text", "")
        return self.content

    @property
    def html(self) -> str:
        """Get HTML content."""
        if isinstance(self.content, dict):
            return self.content.get("html", "")
        return self.content

    @property
    def json(self) -> Dict[str, Any]:
        """Get structured JSON content."""
        if isinstance(self.content, dict):
            return self.content.get("json", {})
        return {}

    @property
    def markdown_content(self) -> str:
        """Get markdown content."""
        if isinstance(self.content, dict):
            return self.content.get("markdown", "")
        return ""

    @property
    def credits_used(self) -> int:
        """Get credits used (legacy compatibility)."""
        if self.billing:
            return self.billing.total_credits
        return 0

    @property
    def tier_used(self) -> str:
        """Get tier used."""
        if self.billing:
            return self.billing.tier_used
        return "1"


@dataclass
class CostEstimate:
    """Cost estimation for a scrape request."""

    url: str
    estimated_tier: str
    estimated_credits: int
    confidence: Literal["low", "medium", "high"]
    max_possible_credits: int
    reasoning: str

    @property
    def estimated_cost_dollars(self) -> float:
        """Get estimated cost in dollars."""
        tier_costs = {"1": 0.0002, "2": 0.0003, "3": 0.0005, "4": 0.001, "5": 0.02}
        return tier_costs.get(self.estimated_tier, 0.0003)


@dataclass
class UsageStats:
    """Account usage statistics."""

    credits_available: int
    credits_used_month: int
    credits_limit: int
    plan: str
    period_start: str
    period_end: str

    @property
    def balance_dollars(self) -> float:
        """Get balance in dollars (microcents to dollars)."""
        return self.credits_available / 1_000_000


@dataclass
class JobStatus:
    """Status of an async scrape job."""

    job_id: str
    status: Literal["pending", "running", "succeeded", "failed"]
    result: Optional[ScrapeResult] = None
    error: Optional[str] = None


# =============================================================================
# CLIENT
# =============================================================================


class AlterLab:
    """AlterLab API client.

    Example:
        # Synchronous usage
        client = AlterLab(api_key="sk_live_...")
        result = client.scrape("https://example.com")
        print(result.text)

        # With options
        result = client.scrape(
            "https://example.com",
            mode="js",
            advanced=AdvancedOptions(render_js=True, screenshot=True),
        )
        print(result.screenshot_url)

        # Cost estimation
        estimate = client.estimate_cost("https://linkedin.com")
        print(f"Estimated: ${estimate.estimated_cost_dollars:.4f}")
    """

    DEFAULT_BASE_URL = "https://api.alterlab.io"
    DEFAULT_TIMEOUT = 120
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_RETRY_DELAY = 1.0

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: int = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        retry_delay: float = DEFAULT_RETRY_DELAY,
    ):
        """Initialize AlterLab client.

        Args:
            api_key: Your API key. If not provided, reads from ALTERLAB_API_KEY env var.
            base_url: API base URL. Defaults to https://api.alterlab.io
            timeout: Default request timeout in seconds.
            max_retries: Maximum number of retries for transient failures.
            retry_delay: Initial delay between retries (exponential backoff).

        Raises:
            ValueError: If no API key is provided or found in environment.
        """
        self.api_key = api_key or os.environ.get("ALTERLAB_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key required. Pass api_key or set ALTERLAB_API_KEY environment variable."
            )

        self.base_url = (base_url or self.DEFAULT_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay

        self._client: Optional[httpx.Client] = None
        self._async_client: Optional[httpx.AsyncClient] = None

    def _get_client(self) -> httpx.Client:
        """Get or create synchronous HTTP client."""
        if self._client is None:
            self._client = httpx.Client(
                base_url=self.base_url,
                headers={
                    "X-API-Key": self.api_key,
                    "User-Agent": f"AlterLab-Python-SDK/{__version__}",
                    "Content-Type": "application/json",
                },
                timeout=httpx.Timeout(self.timeout),
            )
        return self._client

    def _get_async_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "X-API-Key": self.api_key,
                    "User-Agent": f"AlterLab-Python-SDK/{__version__}",
                    "Content-Type": "application/json",
                },
                timeout=httpx.Timeout(self.timeout),
            )
        return self._async_client

    def _handle_error_response(self, response: httpx.Response) -> None:
        """Convert HTTP error responses to appropriate exceptions."""
        try:
            data = response.json()
            detail = data.get("detail", response.text)
        except Exception:
            detail = response.text

        if response.status_code == 401:
            raise AuthenticationError(401, detail, response)
        elif response.status_code == 402:
            raise InsufficientCreditsError(402, detail, response)
        elif response.status_code == 422:
            raise ValidationError(422, detail, response)
        elif response.status_code == 429:
            retry_after = response.headers.get("Retry-After")
            raise RateLimitError(
                detail,
                retry_after=int(retry_after) if retry_after else None,
                response=response,
            )
        elif response.status_code >= 400:
            raise AlterLabAPIError(response.status_code, detail, response)

    def _request_with_retry(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> httpx.Response:
        """Make HTTP request with retry logic."""
        client = self._get_client()
        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries):
            try:
                response = client.request(method, path, **kwargs)

                if response.status_code >= 400:
                    # Don't retry client errors (4xx) except rate limits
                    if 400 <= response.status_code < 500 and response.status_code != 429:
                        self._handle_error_response(response)

                    # Retry server errors and rate limits
                    last_error = AlterLabAPIError(
                        response.status_code,
                        response.text,
                        response,
                    )

                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        time.sleep(float(retry_after))
                    else:
                        time.sleep(self.retry_delay * (2**attempt))
                    continue

                return response

            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last_error = AlterLabError(f"Network error: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay * (2**attempt))
                continue

        raise last_error or AlterLabError("Request failed after retries")

    async def _async_request_with_retry(
        self,
        method: str,
        path: str,
        **kwargs,
    ) -> httpx.Response:
        """Make async HTTP request with retry logic."""
        client = self._get_async_client()
        last_error: Optional[Exception] = None

        for attempt in range(self.max_retries):
            try:
                response = await client.request(method, path, **kwargs)

                if response.status_code >= 400:
                    if 400 <= response.status_code < 500 and response.status_code != 429:
                        self._handle_error_response(response)

                    last_error = AlterLabAPIError(
                        response.status_code,
                        response.text,
                        response,
                    )

                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        await asyncio.sleep(float(retry_after))
                    else:
                        await asyncio.sleep(self.retry_delay * (2**attempt))
                    continue

                return response

            except (httpx.TimeoutException, httpx.NetworkError) as e:
                last_error = AlterLabError(f"Network error: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2**attempt))
                continue

        raise last_error or AlterLabError("Request failed after retries")

    def _parse_scrape_response(self, data: Dict[str, Any]) -> ScrapeResult:
        """Parse API response into ScrapeResult."""
        billing_data = data.get("billing", {})
        billing = BillingDetails(
            total_credits=billing_data.get("total_credits", 0),
            tier_used=billing_data.get("tier_used", "1"),
            escalations=[
                TierEscalation(
                    tier=e.get("tier", "1"),
                    result=e.get("result", "success"),
                    credits=e.get("credits", 0),
                    duration_ms=e.get("duration_ms"),
                    error=e.get("error"),
                )
                for e in billing_data.get("escalations", [])
            ],
            savings=billing_data.get("savings", 0),
            optimization_suggestion=billing_data.get("optimization_suggestion"),
            byop_applied=billing_data.get("byop_applied", False),
            byop_discount_percent=billing_data.get("byop_discount_percent"),
            original_cost_microcents=billing_data.get("original_cost_microcents"),
            final_cost_microcents=billing_data.get("final_cost_microcents"),
        )

        return ScrapeResult(
            url=data.get("url", ""),
            status_code=data.get("status_code", 200),
            content=data.get("content", ""),
            title=data.get("title"),
            author=data.get("author"),
            published_at=data.get("published_at"),
            metadata=data.get("metadata", {}),
            headers=data.get("headers", {}),
            cached=data.get("cached", False),
            cached_at=data.get("cached_at"),
            expires_at=data.get("expires_at"),
            response_time_ms=data.get("response_time_ms", 0),
            size_bytes=data.get("size_bytes", 0),
            raw_html=data.get("raw_html"),
            screenshot_url=data.get("screenshot_url"),
            pdf_url=data.get("pdf_url"),
            ocr_results=data.get("ocr_results"),
            proxy_used=data.get("proxy_used"),
            filtered_content=data.get("filtered_content"),
            billing=billing,
            extraction_method=data.get("extraction_method", "algorithmic"),
            method_details=data.get("method_details"),
        )

    def _build_scrape_payload(
        self,
        url: str,
        mode: Literal["auto", "html", "js", "pdf", "ocr"] = "auto",
        sync: bool = True,
        advanced: Optional[AdvancedOptions] = None,
        cost_controls: Optional[CostControls] = None,
        cache: bool = False,
        cache_ttl: Optional[int] = None,
        force_refresh: bool = False,
        include_raw_html: bool = False,
        timeout: Optional[int] = None,
        formats: Optional[List[Literal["text", "json", "html", "markdown"]]] = None,
        extraction_schema: Optional[Dict[str, Any]] = None,
        extraction_prompt: Optional[str] = None,
        extraction_profile: Optional[
            Literal["auto", "product", "article", "job_posting", "faq", "recipe", "event"]
        ] = None,
        evidence: bool = False,
        promote_schema_org: bool = True,
        wait_for: Optional[str] = None,
        screenshot: bool = False,
        wait_until: str = "networkidle",
        enable_scroll: Optional[bool] = None,
        pdf_format: str = "markdown",
        ocr_language: str = "eng",
    ) -> Dict[str, Any]:
        """Build the request payload for scraping."""
        payload: Dict[str, Any] = {
            "url": url,
            "mode": mode,
            "sync": sync,
            "cache": cache,
            "force_refresh": force_refresh,
            "include_raw_html": include_raw_html,
            "timeout": timeout or self.timeout,
            "evidence": evidence,
            "promote_schema_org": promote_schema_org,
            "wait_until": wait_until,
        }

        if cache_ttl is not None:
            payload["cache_ttl"] = cache_ttl

        if advanced:
            payload["advanced"] = advanced.to_dict()

        if cost_controls:
            payload["cost_controls"] = cost_controls.to_dict()

        if formats:
            payload["formats"] = formats

        if extraction_schema:
            payload["extraction_schema"] = extraction_schema

        if extraction_prompt:
            payload["extraction_prompt"] = extraction_prompt

        if extraction_profile:
            payload["extraction_profile"] = extraction_profile

        if wait_for:
            payload["wait_for"] = wait_for

        if screenshot:
            payload["screenshot"] = screenshot

        if enable_scroll is not None:
            payload["enable_scroll"] = enable_scroll

        if mode == "pdf":
            payload["pdf_format"] = pdf_format

        if mode == "ocr":
            payload["ocr_language"] = ocr_language

        return payload

    # =========================================================================
    # SYNCHRONOUS API
    # =========================================================================

    def scrape(
        self,
        url: str,
        mode: Literal["auto", "html", "js", "pdf", "ocr"] = "auto",
        sync: bool = True,
        advanced: Optional[AdvancedOptions] = None,
        cost_controls: Optional[CostControls] = None,
        cache: bool = False,
        cache_ttl: Optional[int] = None,
        force_refresh: bool = False,
        include_raw_html: bool = False,
        timeout: Optional[int] = None,
        formats: Optional[List[Literal["text", "json", "html", "markdown"]]] = None,
        extraction_schema: Optional[Dict[str, Any]] = None,
        extraction_prompt: Optional[str] = None,
        extraction_profile: Optional[
            Literal["auto", "product", "article", "job_posting", "faq", "recipe", "event"]
        ] = None,
        evidence: bool = False,
        promote_schema_org: bool = True,
        wait_for: Optional[str] = None,
        screenshot: bool = False,
        wait_until: str = "networkidle",
        enable_scroll: Optional[bool] = None,
        pdf_format: str = "markdown",
        ocr_language: str = "eng",
        poll_interval: float = 0.5,
        poll_timeout: float = 300.0,
    ) -> ScrapeResult:
        """Scrape a URL.

        Args:
            url: URL to scrape.
            mode: Scraping mode ('auto', 'html', 'js', 'pdf', 'ocr').
            sync: Wait for result (True) or return job ID immediately (False).
            advanced: Advanced scraping options.
            cost_controls: Cost control parameters.
            cache: Enable caching (opt-in, default False).
            cache_ttl: Cache TTL in seconds (60-86400).
            force_refresh: Bypass cache even if cache=True.
            include_raw_html: Include raw HTML in response.
            timeout: Request timeout in seconds.
            formats: Output formats ('text', 'json', 'html', 'markdown').
            extraction_schema: JSON Schema for structured extraction.
            extraction_prompt: Natural language extraction instructions.
            extraction_profile: Pre-defined extraction profile.
            evidence: Include provenance for extracted fields.
            promote_schema_org: Use Schema.org as primary structure.
            wait_for: CSS selector to wait for (JS mode).
            screenshot: Capture screenshot (JS mode).
            wait_until: Wait condition ('domcontentloaded', 'networkidle', 'load').
            enable_scroll: Enable scrolling for lazy-loaded images.
            pdf_format: PDF output format ('text', 'markdown').
            ocr_language: OCR language code (e.g., 'eng', 'fra').
            poll_interval: Job polling interval in seconds.
            poll_timeout: Maximum time to wait for job completion.

        Returns:
            ScrapeResult with content, metadata, and billing details.

        Raises:
            AuthenticationError: Invalid API key.
            InsufficientCreditsError: Not enough balance.
            RateLimitError: Rate limit exceeded.
            ValidationError: Invalid request parameters.
            ScrapeError: Scraping failed.
            TimeoutError: Job timed out.
        """
        payload = self._build_scrape_payload(
            url=url,
            mode=mode,
            sync=sync,
            advanced=advanced,
            cost_controls=cost_controls,
            cache=cache,
            cache_ttl=cache_ttl,
            force_refresh=force_refresh,
            include_raw_html=include_raw_html,
            timeout=timeout,
            formats=formats,
            extraction_schema=extraction_schema,
            extraction_prompt=extraction_prompt,
            extraction_profile=extraction_profile,
            evidence=evidence,
            promote_schema_org=promote_schema_org,
            wait_for=wait_for,
            screenshot=screenshot,
            wait_until=wait_until,
            enable_scroll=enable_scroll,
            pdf_format=pdf_format,
            ocr_language=ocr_language,
        )

        response = self._request_with_retry("POST", "/api/v1/scrape", json=payload)
        data = response.json()

        # Handle async response (202 with job_id)
        if response.status_code == 202 and "job_id" in data:
            if not sync:
                # Return job info for manual polling
                return ScrapeResult(
                    url=url,
                    status_code=202,
                    content={"job_id": data["job_id"]},
                    metadata={"job_id": data["job_id"]},
                )

            # Poll for completion
            return self.wait_for_job(
                data["job_id"],
                poll_interval=poll_interval,
                poll_timeout=poll_timeout,
            )

        return self._parse_scrape_response(data)

    def wait_for_job(
        self,
        job_id: str,
        poll_interval: float = 0.5,
        poll_timeout: float = 300.0,
    ) -> ScrapeResult:
        """Wait for an async job to complete.

        Args:
            job_id: Job ID to poll.
            poll_interval: Polling interval in seconds.
            poll_timeout: Maximum wait time in seconds.

        Returns:
            ScrapeResult when job completes.

        Raises:
            TimeoutError: Job didn't complete within timeout.
            ScrapeError: Job failed.
        """
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            if elapsed > poll_timeout:
                raise TimeoutError(
                    f"Job {job_id} did not complete within {poll_timeout} seconds"
                )

            status = self.get_job_status(job_id)

            if status.status == "succeeded":
                if status.result:
                    return status.result
                raise ScrapeError(200, "Job completed but no result returned")

            elif status.status == "failed":
                raise ScrapeError(
                    422,
                    status.error or "Job failed",
                    code="JOB_FAILED",
                )

            time.sleep(poll_interval)

    def get_job_status(self, job_id: str) -> JobStatus:
        """Get the status of an async job.

        Args:
            job_id: Job ID to check.

        Returns:
            JobStatus with current status and result if complete.
        """
        response = self._request_with_retry("GET", f"/api/v1/jobs/{job_id}")
        data = response.json()

        result = None
        if data.get("status") in ("succeeded", "completed") and data.get("result"):
            result = self._parse_scrape_response(data["result"])

        return JobStatus(
            job_id=job_id,
            status=data.get("status", "pending"),
            result=result,
            error=data.get("error"),
        )

    def estimate_cost(
        self,
        url: str,
        mode: Literal["auto", "html", "js", "pdf", "ocr"] = "auto",
        advanced: Optional[AdvancedOptions] = None,
        cost_controls: Optional[CostControls] = None,
    ) -> CostEstimate:
        """Estimate the cost of a scrape request.

        Args:
            url: URL to estimate.
            mode: Scraping mode.
            advanced: Advanced options to include in estimate.
            cost_controls: Cost control parameters.

        Returns:
            CostEstimate with estimated tier, credits, and confidence.
        """
        payload: Dict[str, Any] = {"url": url, "mode": mode}

        if advanced:
            payload["advanced"] = advanced.to_dict()
        if cost_controls:
            payload["cost_controls"] = cost_controls.to_dict()

        response = self._request_with_retry(
            "POST", "/api/v1/scrape/estimate", json=payload
        )
        data = response.json()

        return CostEstimate(
            url=data.get("url", url),
            estimated_tier=data.get("estimated_tier", "2"),
            estimated_credits=data.get("estimated_credits", 2),
            confidence=data.get("confidence", "medium"),
            max_possible_credits=data.get("max_possible_credits", 20),
            reasoning=data.get("reasoning", ""),
        )

    def get_usage(self) -> UsageStats:
        """Get current usage statistics and balance.

        Returns:
            UsageStats with credits, plan, and billing period info.
        """
        response = self._request_with_retry("GET", "/api/v1/usage")
        data = response.json()

        return UsageStats(
            credits_available=data.get("credits_available", 0),
            credits_used_month=data.get("credits_used_month", 0),
            credits_limit=data.get("credits_limit", 0),
            plan=data.get("plan", ""),
            period_start=data.get("period_start", ""),
            period_end=data.get("period_end", ""),
        )

    # =========================================================================
    # CONVENIENCE METHODS
    # =========================================================================

    def scrape_html(self, url: str, **kwargs) -> ScrapeResult:
        """Scrape HTML content without JavaScript rendering.

        This is the fastest and cheapest option (Tier 1: $0.0002/request).

        Args:
            url: URL to scrape.
            **kwargs: Additional arguments passed to scrape().

        Returns:
            ScrapeResult with HTML content.
        """
        return self.scrape(url, mode="html", **kwargs)

    def scrape_js(
        self,
        url: str,
        screenshot: bool = False,
        wait_for: Optional[str] = None,
        **kwargs,
    ) -> ScrapeResult:
        """Scrape with JavaScript rendering.

        Uses Playwright browser automation (Tier 4: $0.001/request).

        Args:
            url: URL to scrape.
            screenshot: Capture full-page screenshot.
            wait_for: CSS selector to wait for before capturing.
            **kwargs: Additional arguments passed to scrape().

        Returns:
            ScrapeResult with rendered content.
        """
        advanced = kwargs.pop("advanced", None) or AdvancedOptions(render_js=True)
        if not advanced.render_js:
            advanced.render_js = True
        if screenshot:
            advanced.screenshot = True

        return self.scrape(
            url, mode="js", advanced=advanced, wait_for=wait_for, **kwargs
        )

    def scrape_pdf(
        self,
        url: str,
        format: Literal["text", "markdown"] = "markdown",
        **kwargs,
    ) -> ScrapeResult:
        """Extract content from PDF files.

        Args:
            url: PDF URL.
            format: Output format ('text' or 'markdown').
            **kwargs: Additional arguments passed to scrape().

        Returns:
            ScrapeResult with extracted PDF content.
        """
        return self.scrape(url, mode="pdf", pdf_format=format, **kwargs)

    def scrape_ocr(
        self,
        url: str,
        language: str = "eng",
        **kwargs,
    ) -> ScrapeResult:
        """Extract text from images using OCR.

        Args:
            url: Image URL.
            language: OCR language code (e.g., 'eng', 'fra', 'deu').
            **kwargs: Additional arguments passed to scrape().

        Returns:
            ScrapeResult with OCR-extracted text.
        """
        return self.scrape(url, mode="ocr", ocr_language=language, **kwargs)

    # =========================================================================
    # ASYNC API
    # =========================================================================

    async def scrape_async(
        self,
        url: str,
        mode: Literal["auto", "html", "js", "pdf", "ocr"] = "auto",
        sync: bool = True,
        advanced: Optional[AdvancedOptions] = None,
        cost_controls: Optional[CostControls] = None,
        cache: bool = False,
        cache_ttl: Optional[int] = None,
        force_refresh: bool = False,
        include_raw_html: bool = False,
        timeout: Optional[int] = None,
        formats: Optional[List[Literal["text", "json", "html", "markdown"]]] = None,
        extraction_schema: Optional[Dict[str, Any]] = None,
        extraction_prompt: Optional[str] = None,
        extraction_profile: Optional[
            Literal["auto", "product", "article", "job_posting", "faq", "recipe", "event"]
        ] = None,
        evidence: bool = False,
        promote_schema_org: bool = True,
        wait_for: Optional[str] = None,
        screenshot: bool = False,
        wait_until: str = "networkidle",
        enable_scroll: Optional[bool] = None,
        pdf_format: str = "markdown",
        ocr_language: str = "eng",
        poll_interval: float = 0.5,
        poll_timeout: float = 300.0,
    ) -> ScrapeResult:
        """Async version of scrape(). See scrape() for full documentation."""
        payload = self._build_scrape_payload(
            url=url,
            mode=mode,
            sync=sync,
            advanced=advanced,
            cost_controls=cost_controls,
            cache=cache,
            cache_ttl=cache_ttl,
            force_refresh=force_refresh,
            include_raw_html=include_raw_html,
            timeout=timeout,
            formats=formats,
            extraction_schema=extraction_schema,
            extraction_prompt=extraction_prompt,
            extraction_profile=extraction_profile,
            evidence=evidence,
            promote_schema_org=promote_schema_org,
            wait_for=wait_for,
            screenshot=screenshot,
            wait_until=wait_until,
            enable_scroll=enable_scroll,
            pdf_format=pdf_format,
            ocr_language=ocr_language,
        )

        response = await self._async_request_with_retry(
            "POST", "/api/v1/scrape", json=payload
        )
        data = response.json()

        if response.status_code == 202 and "job_id" in data:
            if not sync:
                return ScrapeResult(
                    url=url,
                    status_code=202,
                    content={"job_id": data["job_id"]},
                    metadata={"job_id": data["job_id"]},
                )

            return await self.wait_for_job_async(
                data["job_id"],
                poll_interval=poll_interval,
                poll_timeout=poll_timeout,
            )

        return self._parse_scrape_response(data)

    async def wait_for_job_async(
        self,
        job_id: str,
        poll_interval: float = 0.5,
        poll_timeout: float = 300.0,
    ) -> ScrapeResult:
        """Async version of wait_for_job()."""
        start_time = time.time()

        while True:
            elapsed = time.time() - start_time
            if elapsed > poll_timeout:
                raise TimeoutError(
                    f"Job {job_id} did not complete within {poll_timeout} seconds"
                )

            status = await self.get_job_status_async(job_id)

            if status.status == "succeeded":
                if status.result:
                    return status.result
                raise ScrapeError(200, "Job completed but no result returned")

            elif status.status == "failed":
                raise ScrapeError(
                    422,
                    status.error or "Job failed",
                    code="JOB_FAILED",
                )

            await asyncio.sleep(poll_interval)

    async def get_job_status_async(self, job_id: str) -> JobStatus:
        """Async version of get_job_status()."""
        response = await self._async_request_with_retry(
            "GET", f"/api/v1/jobs/{job_id}"
        )
        data = response.json()

        result = None
        if data.get("status") in ("succeeded", "completed") and data.get("result"):
            result = self._parse_scrape_response(data["result"])

        return JobStatus(
            job_id=job_id,
            status=data.get("status", "pending"),
            result=result,
            error=data.get("error"),
        )

    async def estimate_cost_async(
        self,
        url: str,
        mode: Literal["auto", "html", "js", "pdf", "ocr"] = "auto",
        advanced: Optional[AdvancedOptions] = None,
        cost_controls: Optional[CostControls] = None,
    ) -> CostEstimate:
        """Async version of estimate_cost()."""
        payload: Dict[str, Any] = {"url": url, "mode": mode}

        if advanced:
            payload["advanced"] = advanced.to_dict()
        if cost_controls:
            payload["cost_controls"] = cost_controls.to_dict()

        response = await self._async_request_with_retry(
            "POST", "/api/v1/scrape/estimate", json=payload
        )
        data = response.json()

        return CostEstimate(
            url=data.get("url", url),
            estimated_tier=data.get("estimated_tier", "2"),
            estimated_credits=data.get("estimated_credits", 2),
            confidence=data.get("confidence", "medium"),
            max_possible_credits=data.get("max_possible_credits", 20),
            reasoning=data.get("reasoning", ""),
        )

    async def get_usage_async(self) -> UsageStats:
        """Async version of get_usage()."""
        response = await self._async_request_with_retry("GET", "/api/v1/usage")
        data = response.json()

        return UsageStats(
            credits_available=data.get("credits_available", 0),
            credits_used_month=data.get("credits_used_month", 0),
            credits_limit=data.get("credits_limit", 0),
            plan=data.get("plan", ""),
            period_start=data.get("period_start", ""),
            period_end=data.get("period_end", ""),
        )

    # =========================================================================
    # CONTEXT MANAGERS
    # =========================================================================

    def close(self) -> None:
        """Close HTTP clients and release resources."""
        if self._client:
            self._client.close()
            self._client = None
        if self._async_client:
            # For sync close of async client
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self._async_client.aclose())
                else:
                    loop.run_until_complete(self._async_client.aclose())
            except RuntimeError:
                pass
            self._async_client = None

    async def aclose(self) -> None:
        """Async close of HTTP clients."""
        if self._client:
            self._client.close()
            self._client = None
        if self._async_client:
            await self._async_client.aclose()
            self._async_client = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.aclose()


# =============================================================================
# ASYNC CLIENT ALIAS
# =============================================================================


class AsyncAlterLab(AlterLab):
    """Async-first AlterLab client.

    Provides async methods as the primary API for use with asyncio.

    Example:
        async with AsyncAlterLab(api_key="sk_live_...") as client:
            result = await client.scrape("https://example.com")
            print(result.text)

            # Concurrent scraping
            urls = ["https://example.com/1", "https://example.com/2"]
            results = await asyncio.gather(*[client.scrape(url) for url in urls])
    """

    async def scrape(self, url: str, **kwargs) -> ScrapeResult:
        """Scrape a URL (async)."""
        return await self.scrape_async(url, **kwargs)

    async def wait_for_job(self, job_id: str, **kwargs) -> ScrapeResult:
        """Wait for job completion (async)."""
        return await self.wait_for_job_async(job_id, **kwargs)

    async def get_job_status(self, job_id: str) -> JobStatus:
        """Get job status (async)."""
        return await self.get_job_status_async(job_id)

    async def estimate_cost(self, url: str, **kwargs) -> CostEstimate:
        """Estimate cost (async)."""
        return await self.estimate_cost_async(url, **kwargs)

    async def get_usage(self) -> UsageStats:
        """Get usage stats (async)."""
        return await self.get_usage_async()

    async def scrape_html(self, url: str, **kwargs) -> ScrapeResult:
        """Scrape HTML (async)."""
        return await self.scrape(url, mode="html", **kwargs)

    async def scrape_js(
        self,
        url: str,
        screenshot: bool = False,
        wait_for: Optional[str] = None,
        **kwargs,
    ) -> ScrapeResult:
        """Scrape with JS rendering (async)."""
        advanced = kwargs.pop("advanced", None) or AdvancedOptions(render_js=True)
        if not advanced.render_js:
            advanced.render_js = True
        if screenshot:
            advanced.screenshot = True

        return await self.scrape(
            url, mode="js", advanced=advanced, wait_for=wait_for, **kwargs
        )

    async def scrape_pdf(
        self,
        url: str,
        format: Literal["text", "markdown"] = "markdown",
        **kwargs,
    ) -> ScrapeResult:
        """Scrape PDF (async)."""
        return await self.scrape(url, mode="pdf", pdf_format=format, **kwargs)

    async def scrape_ocr(
        self,
        url: str,
        language: str = "eng",
        **kwargs,
    ) -> ScrapeResult:
        """Scrape with OCR (async)."""
        return await self.scrape(url, mode="ocr", ocr_language=language, **kwargs)
