/**
 * AlterLab SDK Quick Start Examples
 *
 * Run with: npx ts-node examples/quickstart.ts
 */

import { AlterLab, ScrapeError, AuthenticationError } from '../src';

async function main() {
  // Initialize client (uses ALTERLAB_API_KEY env var or pass directly)
  const client = new AlterLab({ apiKey: process.env.ALTERLAB_API_KEY });

  console.log('=== Basic Scraping ===\n');

  // Simple scrape
  const result = await client.scrape('https://example.com');
  console.log(`Title: ${result.title}`);
  console.log(`Text length: ${result.text.length} chars`);
  console.log(`Cost: $${result.billing.costDollars.toFixed(4)}`);
  console.log(`Tier used: ${result.billing.tierName} (${result.billing.tierUsed})`);

  console.log('\n=== Check Usage ===\n');

  // Get account balance
  const usage = await client.getUsage();
  console.log(`Balance: $${usage.balanceDollars.toFixed(2)}`);
  console.log(`Requests this month: ${usage.requestsMonth}`);

  console.log('\n=== Cost Estimation ===\n');

  // Estimate cost before scraping
  const estimate = await client.estimateCost('https://linkedin.com');
  console.log(`Estimated tier: ${estimate.tierName}`);
  console.log(`Estimated cost: $${estimate.estimatedCostDollars.toFixed(4)}`);
  console.log(`Confidence: ${estimate.confidence}`);

  console.log('\n=== Structured Extraction ===\n');

  // Extract specific fields
  const productResult = await client.scrape('https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html', {
    extractionSchema: {
      type: 'object',
      properties: {
        title: { type: 'string' },
        price: { type: 'string' },
        availability: { type: 'string' }
      }
    }
  });

  console.log('Extracted data:', JSON.stringify(productResult.json, null, 2));

  console.log('\n=== Done! ===');
}

// Run with error handling
main().catch((error) => {
  if (error instanceof AuthenticationError) {
    console.error('Authentication failed. Check your API key.');
  } else if (error instanceof ScrapeError) {
    console.error(`Scraping failed: ${error.message}`);
  } else {
    console.error('Error:', error);
  }
  process.exit(1);
});
