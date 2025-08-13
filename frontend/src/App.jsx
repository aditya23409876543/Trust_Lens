import React, { useEffect, useState } from "react";
import { API_URL } from "./config";

export default function App() {
  // State to hold the list of products
  const [products, setProducts] = useState([]);
  // State to hold feedback for each product, keyed by product ID
  const [feedbacks, setFeedbacks] = useState({});

  // Effect hook to fetch data when the component mounts
  useEffect(() => {
    // Fetch the list of all products
    fetch(`${API_URL}/api/v1/products/`)
      .then((res) => res.json())
      .then((data) => {
        setProducts(data);

        // After getting products, fetch feedback for each one
        data.forEach((p) => {
          fetch(`${API_URL}/api/v1/products/${p.id}/feedback`)
            .then((res) => res.json())
            .then((fb) => {
              // Update the feedbacks state, adding the new feedback
              // using the product ID as the key.
              setFeedbacks((prev) => ({ ...prev, [p.id]: fb }));
            });
        });
      });
  }, []); // Empty dependency array means this effect runs once on mount

  return (
    <div style={{ padding: "2rem", fontFamily: "Arial" }}>
      <h1>Product Dashboard</h1>
      {/* Map over the products and display each one */}
      {products.map((product) => (
        <div key={product.id} style={{ marginBottom: "2rem" }}>
          <h2>
            {product.name} - ${product.price}
          </h2>
          <h3>Feedback:</h3>
          {/* Check if feedback for the current product exists and has items */}
          {feedbacks[product.id] && feedbacks[product.id].length > 0 ? (
            <ul>
              {/* Map over the feedback items and display them */}
              {feedbacks[product.id].map((fb) => (
                <li key={fb.id}>
                  Buyer {fb.buyer_id} | Seller {fb.seller_id} | Rating: {fb.rating} | Comment: {fb.comment} | Date: {new Date(fb.date).toLocaleString()}
                </li>
              ))}
            </ul>
          ) : (
            <p>No feedback yet.</p>
          )}
        </div>
      ))}
    </div>
  );
}
