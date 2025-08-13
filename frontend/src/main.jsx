import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

// Find the root element in the DOM.
const rootElement = document.getElementById('root');

// The safest approach: check if the element actually exists before rendering.
if (rootElement) {
  // Create a React root for the container element.
  const root = ReactDOM.createRoot(rootElement);
  
  // Render the main App component inside the root.
  root.render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
} else {
  // If the root element doesn't exist, throw a clear error.
  throw new Error("Could not find the root element with id 'root'.");
}
