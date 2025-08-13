// --- Interactive Particle Background Logic ---

const canvas = document.getElementById('particle-canvas');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let particlesArray;
let isFalling = false;

const mouse = {
    x: null,
    y: null,
    radius: (canvas.height / 120) * (canvas.width / 120)
};

window.addEventListener('mousemove', (event) => {
    mouse.x = event.x;
    mouse.y = event.y;
});

const logoImage = document.getElementById('logo-image');
if (logoImage) {
    logoImage.addEventListener('mouseover', () => {
        isFalling = true;
    });
    logoImage.addEventListener('mouseout', () => {
        isFalling = false;
    });
}


class Particle {
    constructor(x, y, directionX, directionY, size) {
        this.x = x;
        this.y = y;
        this.directionX = directionX;
        this.directionY = directionY;
        this.size = size;
        this.density = (Math.random() * 5) + 1;
        this.fallSpeed = (this.size / 2) + 0.5;
    }
    
    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2, false);
        ctx.fillStyle = 'rgba(255, 255, 255, 0.8)';
        ctx.fill();
    }

    update() {
        if (isFalling) {
            this.y += this.fallSpeed;
            this.x += this.directionX * 1000; 
        } else {
            let dx = mouse.x - this.x;
            let dy = mouse.y - this.y;
            let distance = Math.sqrt(dx * dx + dy * dy);
            if (distance < mouse.radius) {
                let forceDirectionX = dx / distance;
                let forceDirectionY = dy / distance;
                let maxDistance = mouse.radius;
                let force = (maxDistance - distance) / maxDistance;
                let directionX = forceDirectionX * force * this.density;
                let directionY = forceDirectionY * force * this.density;
                this.x -= directionX;
                this.y -= directionY;
            }

            this.x += this.directionX;
            this.y += this.directionY;
        }

        if (this.y > canvas.height) {
            this.y = 0;
            this.x = Math.random() * canvas.width;
        }
        if (this.x > canvas.width) this.x = 0;
        if (this.x < 0) this.x = canvas.width;
        if (this.y < 0) this.y = canvas.height;

        this.draw();
    }
}

function init() {
    particlesArray = [];
    let numberOfParticles = (canvas.height * canvas.width) / 9000;
    for (let i = 0; i < numberOfParticles; i++) {
        let size = (Math.random() * 2) + 1;
        let x = Math.random() * innerWidth;
        let y = Math.random() * innerHeight;
        let directionX = (Math.random() * 0.4) - 0.2;
        let directionY = (Math.random() * 0.4) - 0.2;
        particlesArray.push(new Particle(x, y, directionX, directionY, size));
    }
}

function animate() {
    requestAnimationFrame(animate);
    ctx.clearRect(0, 0, innerWidth, innerHeight);
    for (let i = 0; i < particlesArray.length; i++) {
        particlesArray[i].update();
    }
}

init();
animate();

window.addEventListener('resize', () => {
    canvas.width = innerWidth;
    canvas.height = innerHeight;
    mouse.radius = (canvas.height / 120) * (canvas.width / 120);
    init();
});


// --- Looping Typing Animation Logic ---
document.addEventListener('DOMContentLoaded', function() {
    const typingTitleElement = document.getElementById('typing-title');
    if (typingTitleElement) {
        const textToType = "Welcome to Trust Lens";
        let charIndex = 0;
        let isDeleting = false;

        function typeAnimationLoop() {
            const currentText = textToType;
            
            if (isDeleting) {
                // Erase text
                typingTitleElement.textContent = currentText.substring(0, charIndex - 1);
                charIndex--;
            } else {
                // Type text
                typingTitleElement.textContent = currentText.substring(0, charIndex + 1);
                charIndex++;
            }

            // If text is fully typed, pause then start deleting
            if (!isDeleting && charIndex === currentText.length) {
                isDeleting = true;
                setTimeout(typeAnimationLoop, 2000); // Pause before deleting
            } 
            // If text is fully erased, pause then start typing again
            else if (isDeleting && charIndex === 0) {
                isDeleting = false;
                setTimeout(typeAnimationLoop, 500); // Pause before re-typing
            } 
            // Continue typing/erasing
            else {
                const typingSpeed = isDeleting ? 100 : 150;
                setTimeout(typeAnimationLoop, typingSpeed);
            }
        }
        
        setTimeout(typeAnimationLoop, 500); // Initial delay
    }
});


// --- Trust Lens Modal and Search Logic ---

const launchButton = document.getElementById('launchBtn');
const modalContainer = document.getElementById('modal-container');

launchButton.addEventListener('click', createModal);

function createModal() {
    if (document.querySelector('.modal-overlay')) return;

    const modalHTML = `
        <div class="modal-overlay">
            <div class="modal-content">
                <div class="modal-header">
                    <h2>Trust Lens</h2>
                    <button class="close-btn">&times;</button>
                </div>
                <div class="search-controls">
                    <input type="text" id="productSearchInput" placeholder="e.g., Cricket Bat, Laptop...">
                    <button id="searchProductBtn">Search</button>
                </div>
                <div class="tab-nav">
                    <button class="tab-btn active" data-tab="best-deals">🏆 Best Deals</button>
                    <button class="tab-btn" data-tab="amazon">Amazon</button>
                    <button class="tab-btn" data-tab="flipkart">Flipkart</button>
                    <button class="tab-btn fraud-tab" data-tab="frauds">⚠️ Frauds</button>
                </div>
                <div class="tab-content">
                    <div class="tab-pane active" id="best-deals-content"><p>Enter a product to find the best deals.</p></div>
                    <div class="tab-pane" id="amazon-content"></div>
                    <div class="tab-pane" id="flipkart-content"></div>
                    <div class="tab-pane" id="frauds-content"></div>
                </div>
            </div>
        </div>
    `;

    modalContainer.innerHTML = modalHTML;
    const modalOverlay = document.querySelector('.modal-overlay');
    
    setTimeout(() => modalOverlay.classList.add('active'), 10);

    modalOverlay.querySelector('.close-btn').addEventListener('click', closeModal);
    modalOverlay.querySelector('#searchProductBtn').addEventListener('click', handleProductSearch);
    modalOverlay.addEventListener('click', (event) => {
        if (event.target === modalOverlay) closeModal();
    });

    modalOverlay.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });
}

function closeModal() {
    const modalOverlay = document.querySelector('.modal-overlay');
    if (modalOverlay) {
        modalOverlay.classList.remove('active');
        modalOverlay.addEventListener('transitionend', () => modalOverlay.remove(), { once: true });
    }
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    document.querySelectorAll('.tab-pane').forEach(pane => pane.classList.remove('active'));
    document.querySelector(`.tab-btn[data-tab="${tabId}"]`).classList.add('active');
    document.getElementById(`${tabId}-content`).classList.add('active');
}

async function handleProductSearch() {
    const productName = document.getElementById('productSearchInput').value;
    if (!productName) return alert('Please enter a product name.');

    document.getElementById('best-deals-content').innerHTML = '<p><strong>Searching...</strong></p>';
    document.getElementById('amazon-content').innerHTML = '<p><strong>Searching...</strong></p>';
    document.getElementById('flipkart-content').innerHTML = '<p><strong>Searching...</strong></p>';
    document.getElementById('frauds-content').innerHTML = '<p><strong>Analyzing for suspicious activity...</strong></p>';

    try {
        const response = await fetch(`/api/search?product=${encodeURIComponent(productName)}`);
        if (!response.ok) throw new Error(`Server Error: ${response.status}`);
        
        const data = await response.json();
        
        renderBestDeals(data.bestDeals);
        renderAmazon(data.amazon);
        renderFlipkart(data.flipkart);
        renderFrauds(data.frauds);

    } catch (error) {
        console.error('Search failed:', error);
        document.getElementById('best-deals-content').innerHTML = '<p style="color: red;">Search failed.</p>';
    }
}

function renderBestDeals(sellers) {
    const container = document.getElementById('best-deals-content');
    if (!sellers || sellers.length === 0) {
        container.innerHTML = '<p>No deals found for this product.</p>';
        return;
    }
    container.innerHTML = sellers.map(seller => getSellerCardHTML(seller)).join('');
}

function renderAmazon(sellers) {
    const container = document.getElementById('amazon-content');
    let content = '<div class="platform-header amazon-theme">Amazon Listings</div>';
    if (!sellers || sellers.length === 0) {
        content += '<p>No deals found on Amazon for this product.</p>';
    } else {
        content += sellers.map(seller => getSellerCardHTML(seller)).join('');
    }
    container.innerHTML = content;
}

function renderFlipkart(sellers) {
    const container = document.getElementById('flipkart-content');
    let content = '<div class="platform-header flipkart-theme">Flipkart Listings</div>';
    if (!sellers || sellers.length === 0) {
        content += '<p>No deals found on Flipkart for this product.</p>';
    } else {
        content += sellers.map(seller => getSellerCardHTML(seller)).join('');
    }
    container.innerHTML = content;
}

function renderFrauds(sellers) {
    const container = document.getElementById('frauds-content');
    let content = '<div class="platform-header fraud-theme">Suspicious Listings</div>';
    if (!sellers || sellers.length === 0) {
        content += '<p>No suspicious activity detected for this product. All clear! ✅</p>';
    } else {
        content += sellers.map(seller => getSellerCardHTML(seller)).join('');
    }
    container.innerHTML = content;
}

function getSellerCardHTML(seller) {
    const isSuspicious = seller.fraudRisk && seller.fraudRisk.isSuspicious;
    const fraudWarningHTML = isSuspicious
        ? `<div class="fraud-warning">⚠️ ${seller.fraudRisk.message}</div>`
        : '';

    return `
        <div class="review-card ${isSuspicious ? 'suspicious' : ''}">
            <div class="card-buttons">
                <div class="card-btn btn-red"></div>
                <div class="card-btn btn-yellow"></div>
                <div class="card-btn btn-green"></div>
            </div>
            ${fraudWarningHTML}
            <p>
                <strong><a href="${seller.link}" target="_blank" rel="noopener noreferrer">${seller.sellerName}</a></strong>
                ${seller.platform ? `<span class="meta">on ${seller.platform}</span>` : ''}
            </p>
            <p><strong>Price:</strong> ₹${(seller.price || 0).toFixed(2)}</p>
            <p>
                <span class="rating">Rating: ${seller.rating} ★</span> 
                (${seller.reviews} reviews)
            </p>
            <p class="meta">Value Score: ${(seller.score || 0).toFixed(4)} (Higher is better)</p>
        </div>
    `;
}