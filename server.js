const express = require('express');
const fs = require('fs');

const app = express();
const PORT = 3000;

// Middleware to serve static files from the 'public' directory
app.use(express.static('public'));
// Middleware to parse incoming JSON requests
app.use(express.json());

/**
 * Helper function to load and parse the mock e-commerce database.
 * Includes error handling in case the file is missing or corrupt.
 */
function loadMockEcommerceDB() {
    try {
        const rawData = fs.readFileSync('mock-ecommerce-db.json');
        return JSON.parse(rawData);
    } catch (error) {
        console.error("Error reading or parsing mock-ecommerce-db.json:", error);
        // Return a default empty structure to prevent the server from crashing
        return { products: [] };
    }
}

/**
 * API Endpoint: /api/search
 * This is the main API for the application. It finds products based on a query,
 * calculates a value score for each seller, and returns a structured response.
 */
app.get('/api/search', (req, res) => {
    // Get the product name from the URL query (e.g., /api/search?product=laptop)
    const productNameQuery = req.query.product;
    if (!productNameQuery) {
        return res.status(400).json({ error: 'A product query is required.' });
    }

    console.log(`Searching MOCK database for: "${productNameQuery}"`);
    const db = loadMockEcommerceDB();

    // Find the product in the database that includes the search term (case-insensitive)
    const matchingProduct = db.products.find(p =>
        p.productName.toLowerCase().includes(productNameQuery.toLowerCase())
    );

    let allSellerOptions = [];
    if (matchingProduct) {
        allSellerOptions = matchingProduct.sellers;
    }

    // Calculate the average price for the found product to use in fraud detection
    const averagePrice = allSellerOptions.length > 0
        ? allSellerOptions.reduce((sum, s) => sum + s.price, 0) / allSellerOptions.length
        : 0;

    // Process each seller to calculate a score and check for fraud
    const scoredSellers = allSellerOptions.map(seller => {
        const score = (seller.rating * Math.log10(seller.reviews + 1)) / seller.price;
        const link = seller.productURL || '#';

        // --- Corrected Fraud Detection Logic ---
        let fraudRisk = { isSuspicious: false, message: '' };

        // Rule 1: Price is unusually low for a new, unproven seller.
        if (seller.price < averagePrice * 0.6 && seller.reviews < 100) {
            fraudRisk.isSuspicious = true;
            fraudRisk.message = "Price is unusually low for a new seller.";
        }

        // Rule 2: The seller has a pattern of poor ratings.
        // Using a separate 'if' ensures this rule is always checked.
        if (seller.rating < 3.0 && seller.reviews > 50) {
            fraudRisk.isSuspicious = true;
            fraudRisk.message = "Seller has a high number of poor ratings.";
        }

        return { ...seller, score, link, fraudRisk };
    });

    // Structure the final response object for the frontend
    const responseData = {
        bestDeals: [...scoredSellers].sort((a, b) => b.score - a.score),
        amazon: scoredSellers.filter(s => s.platform === 'Amazon'),
        flipkart: scoredSellers.filter(s => s.platform === 'Flipkart'),
        frauds: scoredSellers.filter(s => s.fraudRisk.isSuspicious)
    };

    console.log(`Found ${responseData.bestDeals.length} total options. Flagged ${responseData.frauds.length} as suspicious.`);
    res.json(responseData);
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server is running at http://localhost:${PORT}`);
    console.log('Mode: Using reliable MOCK database with fraud detection.');
});