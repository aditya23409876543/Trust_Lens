// scraper.js - COMPLETE DEBUGGING VERSION

const puppeteer = require('puppeteer');

async function searchAmazon(productName) {
    console.log("Launching VISIBLE browser for debugging...");
    let browser;
    try {
        browser = await puppeteer.launch({
            headless: false, // <-- This makes the browser window visible.
            slowMo: 50,      // Slows down actions so you can see them.
            args: ['--no-sandbox', '--disable-setuid-sandbox'] // Arguments for compatibility
        });

        const page = await browser.newPage();
        
        // Set a realistic user agent and viewport to appear more like a real user
        await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36');
        await page.setViewport({ width: 1280, height: 800 });

        const url = `https://www.amazon.in/s?k=${encodeURIComponent(productName)}`;
        console.log(`Navigating to: ${url}`);

        await page.goto(url, { waitUntil: 'networkidle2', timeout: 60000 });

        console.log("Page loaded. Looking for search results container...");
        
        // This is a more robust selector that targets a specific data attribute on Amazon's search result items.
        // It is less likely to change than a simple class name.
        const searchResultSelector = '[data-component-type="s-search-result"]';
        await page.waitForSelector(searchResultSelector, { timeout: 30000 });
        
        console.log("Selector found! Extracting data from the page...");
        const products = await page.evaluate((selector) => {
            // UPDATED SELECTORS INSIDE THE BROWSER CONTEXT
            const items = Array.from(document.querySelectorAll(selector));
            const results = [];

            for (const item of items) {
                const titleElement = item.querySelector('h2 a.a-link-normal');
                const priceElement = item.querySelector('.a-price-whole');
                const ratingElement = item.querySelector('.a-icon-star-small');
                const reviewCountElement = item.querySelector('span.a-size-base');
                
                // We only proceed if the core elements (title and price) exist
                if (titleElement && priceElement) {
                    const title = titleElement.innerText;
                    const price = parseFloat(priceElement.innerText.replace(/,/g, ''));
                    const link = 'https://www.amazon.in' + titleElement.getAttribute('href');

                    let rating = 0;
                    // Safely extract rating text
                    if (ratingElement) {
                        const ratingText = ratingElement.innerText;
                        if (ratingText) {
                            rating = parseFloat(ratingText.split(' ')[0]) || 0;
                        }
                    }

                    let reviews = 0;
                    // Safely extract review count
                    if (reviewCountElement) {
                        const reviewText = reviewCountElement.innerText;
                        if(reviewText) {
                           reviews = parseInt(reviewText.replace(/,/g, ''), 10) || 0;
                        }
                    }

                    // Final check to ensure we have valid, numeric data
                    if (!isNaN(price)) {
                        results.push({ title, price, rating, reviews, link });
                    }
                }
            }
            return results;
        }, searchResultSelector); // Pass the selector into the evaluate function

        console.log(`Successfully extracted ${products.length} products.`);
        await browser.close();
        return products;

    } catch (error) {
        console.error("An error occurred during scraping:", error.message);
        if (browser) {
            console.log("The browser window will close in 15 seconds so you can see the final page state.");
            await new Promise(resolve => setTimeout(resolve, 15000)); // Wait 15s
            await browser.close();
        }
        return []; // Return an empty array on failure
    }
}

// Make the function available to other files
module.exports = { searchAmazon };