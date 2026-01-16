"""AlterLab SDK Quickstart Examples.

This file demonstrates all the features of the AlterLab Python SDK v2.0.

Features demonstrated:
- Simple HTML scraping
- JavaScript rendering with screenshots
- PDF extraction
- OCR text extraction
- Cost estimation before scraping
- Cost controls and budget management
- Structured extraction with schemas
- Async job polling
- Batch scraping
- Usage tracking
"""

import asyncio
from alterlab import AlterLab, AdvancedOptions, CostControls


async def example_simple_scraping():
    """Example 1: Simple HTML scraping (fastest, 1 credit)."""
    print("\n" + "="*60)
    print("Example 1: Simple HTML Scraping")
    print("="*60)

    async with AlterLab(api_key="sk_test_...") as client:
        # Simple scraping with default settings
        result = await client.scrape("https://example.com")

        print(f"Status: {result['status_code']}")
        print(f"Title: {result.get('title', 'N/A')}")
        print(f"Content length: {len(result['content'])} characters")
        print(f"Credits used: {result['billing']['total_credits']}")
        print(f"Response time: {result['response_time_ms']}ms")
        print(f"Cached: {result['cached']}")


async def example_javascript_rendering():
    """Example 2: JavaScript rendering with screenshot."""
    print("\n" + "="*60)
    print("Example 2: JavaScript Rendering with Screenshot")
    print("="*60)

    async with AlterLab(api_key="sk_test_...") as client:
        # Render JavaScript and capture screenshot
        result = await client.scrape_js(
            "https://example.com",
            screenshot=True,
            wait_for=".content",  # Wait for specific element
            markdown=True  # Convert to markdown (free)
        )

        print(f"Title: {result.get('title', 'N/A')}")
        print(f"Content length: {len(result['content'])} characters")
        print(f"Screenshot URL: {result.get('screenshot_url', 'N/A')}")
        print(f"Credits used: {result['billing']['total_credits']}")
        print(f"Tier used: {result['billing']['tier_used']}")


async def example_advanced_options():
    """Example 3: Advanced options with custom configuration."""
    print("\n" + "="*60)
    print("Example 3: Advanced Options")
    print("="*60)

    async with AlterLab(api_key="sk_test_...") as client:
        # Configure advanced options
        advanced = AdvancedOptions(
            render_js=True,
            screenshot=True,
            markdown=True,
            use_proxy=True,  # Use premium proxy
            wait_condition="networkidle"
        )

        result = await client.scrape(
            "https://example.com",
            mode="js",
            advanced=advanced
        )

        print(f"Credits used: {result['billing']['total_credits']}")
        print(f"Escalations: {len(result['billing']['escalations'])}")
        for escalation in result['billing']['escalations']:
            print(f"  - Tier {escalation['tier']}: {escalation['result']} ({escalation['credits']} credits)")


async def example_cost_estimation():
    """Example 4: Estimate cost before scraping."""
    print("\n" + "="*60)
    print("Example 4: Cost Estimation")
    print("="*60)

    async with AlterLab(api_key="sk_test_...") as client:
        # Estimate cost before scraping
        estimate = await client.estimate_cost(
            "https://example.com",
            mode="js",
            advanced=AdvancedOptions(render_js=True, screenshot=True)
        )

        print(f"URL: {estimate['url']}")
        print(f"Estimated tier: {estimate['estimated_tier']}")
        print(f"Estimated credits: {estimate['estimated_credits']}")
        print(f"Max possible credits: {estimate['max_possible_credits']}")
        print(f"Confidence: {estimate['confidence']}")
        print(f"Reasoning: {estimate['reasoning']}")

        # Only proceed if cost is acceptable
        if estimate['estimated_credits'] <= 5:
            print("\nCost is acceptable, proceeding with scrape...")
            result = await client.scrape(
                "https://example.com",
                mode="js",
                advanced=AdvancedOptions(render_js=True, screenshot=True)
            )
            print(f"Actual credits used: {result['billing']['total_credits']}")
        else:
            print(f"\nCost too high ({estimate['estimated_credits']} credits), skipping...")


async def example_cost_controls():
    """Example 5: Cost controls and budget limits."""
    print("\n" + "="*60)
    print("Example 5: Cost Controls")
    print("="*60)

    async with AlterLab(api_key="sk_test_...") as client:
        # Set strict cost limits
        cost_controls = CostControls(
            max_credits=5,  # Don't spend more than 5 credits
            max_tier="2",  # Don't escalate beyond tier 2
            fail_fast=True  # Fail immediately if can't succeed within limits
        )

        try:
            result = await client.scrape(
                "https://example.com",
                cost_controls=cost_controls
            )
            print(f"Success! Credits used: {result['billing']['total_credits']}")
        except Exception as e:
            print(f"Failed due to cost limits: {e}")

        # Optimize for cost (try cheaper tiers first)
        cost_controls = CostControls(prefer_cost=True)
        result = await client.scrape(
            "https://example.com",
            cost_controls=cost_controls
        )
        print(f"Cost-optimized scrape used: {result['billing']['total_credits']} credits")

        # Optimize for speed (skip to reliable tier)
        cost_controls = CostControls(prefer_speed=True)
        result = await client.scrape(
            "https://example.com",
            cost_controls=cost_controls
        )
        print(f"Speed-optimized scrape used: {result['billing']['total_credits']} credits")


async def example_structured_extraction():
    """Example 6: Structured data extraction."""
    print("\n" + "="*60)
    print("Example 6: Structured Extraction")
    print("="*60)

    async with AlterLab(api_key="sk_test_...") as client:
        # Method 1: Use pre-defined profile
        result = await client.scrape(
            "https://example.com/product",
            extraction_profile="product"
        )
        print("Using 'product' profile:")
        print(f"Structured content: {result.get('structured_content', 'N/A')}")

        # Method 2: Custom JSON Schema
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "price": {"type": "number"},
                "description": {"type": "string"},
                "availability": {"type": "string"}
            },
            "required": ["title", "price"]
        }

        result = await client.scrape(
            "https://example.com/product",
            extraction_schema=schema,
            evidence=True  # Include provenance for extracted fields
        )
        print("\nUsing custom schema:")
        print(f"Structured content: {result.get('structured_content', 'N/A')}")
        print(f"Extraction method: {result.get('extraction_method', 'N/A')}")

        # Method 3: Natural language prompt
        result = await client.scrape(
            "https://example.com/article",
            extraction_prompt="Extract the article title, author, publication date, and main content"
        )
        print("\nUsing natural language prompt:")
        print(f"Structured content: {result.get('structured_content', 'N/A')}")


async def example_async_polling():
    """Example 7: Async job polling."""
    print("\n" + "="*60)
    print("Example 7: Async Job Polling")
    print("="*60)

    async with AlterLab(api_key="sk_test_...") as client:
        # Start async job (returns immediately with job_id)
        response = await client.scrape(
            "https://example.com",
            sync=False  # Don't wait for completion
        )

        job_id = response["job_id"]
        print(f"Job started: {job_id}")

        # Option 1: Check status manually
        status = await client.get_job_status(job_id)
        print(f"Job status: {status['status']}")

        # Option 2: Wait for completion with automatic polling
        print("Waiting for job completion...")
        result = await client.wait_for_job(
            job_id,
            poll_interval=1.0,  # Start with 1s interval
            poll_timeout=300.0,  # Timeout after 5 minutes
            backoff_multiplier=1.5,  # Increase interval by 1.5x each time
            max_interval=10.0  # Cap at 10s
        )

        print(f"Job completed!")
        print(f"Credits used: {result['billing']['total_credits']}")


async def example_batch_scraping():
    """Example 8: Batch scraping multiple URLs."""
    print("\n" + "="*60)
    print("Example 8: Batch Scraping")
    print("="*60)

    async with AlterLab(api_key="sk_test_...") as client:
        # Submit batch of requests
        requests = [
            {"url": "https://example.com/page1", "mode": "html"},
            {"url": "https://example.com/page2", "mode": "html"},
            {"url": "https://example.com/page3", "mode": "js"},
            {"url": "https://example.com/page4", "mode": "html"},
            {"url": "https://example.com/page5", "mode": "html"}
        ]

        batch = await client.batch_scrape(
            requests,
            webhook_url="https://myapp.com/webhook"  # Optional webhook for notifications
        )

        print(f"Batch ID: {batch['batch_id']}")
        print(f"Total requests: {batch['total_requests']}")
        print(f"Job IDs: {batch['job_ids']}")

        # Poll individual jobs
        print("\nPolling job statuses...")
        for job_id in batch['job_ids']:
            status = await client.get_job_status(job_id)
            print(f"  Job {job_id}: {status['status']}")

        # Wait for all jobs to complete
        print("\nWaiting for all jobs to complete...")
        results = []
        for job_id in batch['job_ids']:
            result = await client.wait_for_job(job_id, poll_timeout=60)
            results.append(result)

        print(f"\nAll jobs completed! Total results: {len(results)}")
        total_credits = sum(r['billing']['total_credits'] for r in results)
        print(f"Total credits used: {total_credits}")


async def example_pdf_and_ocr():
    """Example 9: PDF extraction and OCR."""
    print("\n" + "="*60)
    print("Example 9: PDF and OCR")
    print("="*60)

    async with AlterLab(api_key="sk_test_...") as client:
        # Extract text from PDF
        result = await client.scrape_pdf(
            "https://example.com/document.pdf",
            format="markdown"  # or "text"
        )
        print("PDF extraction:")
        print(f"Content length: {len(result['content'])} characters")
        print(f"Credits used: {result['billing']['total_credits']}")

        # Extract text from image using OCR
        result = await client.scrape_ocr(
            "https://example.com/image.png",
            language="eng"  # English (also supports fra, deu, spa, etc.)
        )
        print("\nOCR extraction:")
        print(f"Content: {result['content'][:200]}...")
        print(f"OCR results: {len(result.get('ocr_results', []))} regions")
        print(f"Credits used: {result['billing']['total_credits']}")


async def example_usage_tracking():
    """Example 10: Usage tracking and credit management."""
    print("\n" + "="*60)
    print("Example 10: Usage Tracking")
    print("="*60)

    async with AlterLab(api_key="sk_test_...") as client:
        # Check current usage
        usage = await client.get_usage()

        print(f"Subscription tier: {usage['subscription_tier']}")
        print(f"Credits available: {usage['credits_available']}")
        print(f"Credits used this period: {usage['credits_used']}")
        print(f"Credits limit: {usage['credits_limit']}")
        print(f"Requests count: {usage['requests_count']}")
        print(f"Billing period: {usage['billing_period_start']} to {usage['billing_period_end']}")

        # Check if we have enough credits before scraping
        if usage['credits_available'] < 10:
            print("\nWarning: Low credit balance!")
        else:
            print(f"\nSufficient credits available ({usage['credits_available']})")


async def example_error_handling():
    """Example 11: Error handling and retries."""
    print("\n" + "="*60)
    print("Example 11: Error Handling")
    print("="*60)

    from alterlab.client import AlterLabAPIError, AlterLabTimeoutError

    async with AlterLab(
        api_key="sk_test_...",
        timeout=30,
        max_retries=3,
        retry_delay=1.0
    ) as client:
        try:
            # This will automatically retry on transient failures
            result = await client.scrape("https://example.com")
            print(f"Success! Credits used: {result['billing']['total_credits']}")

        except AlterLabAPIError as e:
            print(f"API Error {e.status_code}: {e.detail}")
            # Access raw response for debugging
            if e.response:
                print(f"Response headers: {e.response.headers}")

        except AlterLabTimeoutError as e:
            print(f"Timeout: {e}")

        except Exception as e:
            print(f"Unexpected error: {e}")


async def example_convenience_methods():
    """Example 12: Convenience methods."""
    print("\n" + "="*60)
    print("Example 12: Convenience Methods")
    print("="*60)

    async with AlterLab(api_key="sk_test_...") as client:
        # Simple HTML scraping
        result = await client.scrape_html("https://example.com")
        print(f"HTML scraping: {result['billing']['total_credits']} credits")

        # JS rendering with screenshot
        result = await client.scrape_js(
            "https://example.com",
            screenshot=True,
            wait_for=".content"
        )
        print(f"JS scraping: {result['billing']['total_credits']} credits")

        # PDF extraction
        result = await client.scrape_pdf("https://example.com/doc.pdf")
        print(f"PDF extraction: {result['billing']['total_credits']} credits")

        # OCR extraction
        result = await client.scrape_ocr("https://example.com/image.png")
        print(f"OCR extraction: {result['billing']['total_credits']} credits")


async def example_backwards_compatibility():
    """Example 13: Backwards compatibility with deprecated methods."""
    print("\n" + "="*60)
    print("Example 13: Backwards Compatibility")
    print("="*60)

    import warnings

    async with AlterLab(api_key="sk_test_...") as client:
        # Old method (deprecated, but still works)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            result = await client.scrape_light("https://example.com")

            if w:
                print(f"Deprecation warning: {w[0].message}")

            print(f"Result: {result['status_code']}")
            print("\nRecommendation: Use scrape() or scrape_html() instead")


async def example_synchronous_wrapper():
    """Example 14: Synchronous wrapper for non-async code."""
    print("\n" + "="*60)
    print("Example 14: Synchronous Wrapper")
    print("="*60)

    from alterlab.client import AlterLabSync

    # Use synchronous wrapper for non-async code
    with AlterLabSync(api_key="sk_test_...") as client:
        result = client.scrape("https://example.com")
        print(f"Synchronous scrape: {result['status_code']}")
        print(f"Credits used: {result['billing']['total_credits']}")

        usage = client.get_usage()
        print(f"Credits remaining: {usage['credits_available']}")


async def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("AlterLab Python SDK v2.0 - Quickstart Examples")
    print("="*60)

    # Run examples (comment out any you don't want to run)
    await example_simple_scraping()
    await example_javascript_rendering()
    await example_advanced_options()
    await example_cost_estimation()
    await example_cost_controls()
    await example_structured_extraction()
    await example_async_polling()
    await example_batch_scraping()
    await example_pdf_and_ocr()
    await example_usage_tracking()
    await example_error_handling()
    await example_convenience_methods()
    await example_backwards_compatibility()

    # Note: example_synchronous_wrapper() doesn't need await
    print("\nRunning synchronous wrapper example...")
    await asyncio.create_task(example_synchronous_wrapper())

    print("\n" + "="*60)
    print("All examples completed!")
    print("="*60)


if __name__ == "__main__":
    # Run all examples
    asyncio.run(main())
