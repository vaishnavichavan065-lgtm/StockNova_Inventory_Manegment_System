// ============================================
// NETTECH INVENTORY - MAIN JAVASCRIPT FILE
// ============================================

console.log('🚀 Script loaded successfully!');

// ============================================
// PRODUCTS PAGE FUNCTIONS
// ============================================

// Load all products
async function loadProducts() {
    console.log('📦 Loading products...');
    const tbody = document.getElementById('products-table-body');
    if (tbody) {
        tbody.innerHTML = '<tr><td colspan="8" class="empty-state"><div class="icon">⏳</div><p>Loading products...</p></td></tr>';
    }

    try {
        const response = await fetch('/api/products');
        if (!response.ok) throw new Error('Failed to fetch products');
        const products = await response.json();
        console.log('📦 Products loaded:', products.length);
        displayProducts(products);
    } catch (error) {
        console.error('❌ Error loading products:', error);
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="8" class="empty-state"><div class="icon">❌</div><p>Error loading products</p></td></tr>';
        }
    }
}

// Display products in table
function displayProducts(products) {
    const tbody = document.getElementById('products-table-body');
    if (!tbody) return;

    if (!products || products.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="8" class="empty-state">
                    <div class="icon">📦</div>
                    <p>No products found. Add your first product!</p>
                </td>
            </tr>
        `;
        return;
    }

    let html = '';
    products.forEach(p => {
        const statusClass = p.quantity > 10 ? 'in-stock' : p.quantity > 0 ? 'low-stock' : 'out-of-stock';
        const statusText = p.quantity > 10 ? 'In Stock' : p.quantity > 0 ? 'Low Stock' : 'Out of Stock';
        const supplierName = p.supplier_name || '-';

        html += `
            <tr>
                <td>#${p.id}</td>
                <td><strong>${escapeHtml(p.name)}</strong></td>
                <td>${escapeHtml(p.category || '-')}</td>
                <td>${p.quantity}</td>
                <td>₹${(p.price || 0).toFixed(2)}</td>
                <td>${escapeHtml(supplierName)}</td>
                <td><span class="status ${statusClass}">${statusText}</span></td>
                <td>
                    <div class="actions">
                        <a href="/edit-product/${p.id}" class="btn btn-warning btn-sm">Edit</a>
                        <button class="btn btn-danger btn-sm" onclick="deleteProduct(${p.id})">Delete</button>
                    </div>
                </td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}

// Search products
async function searchProducts() {
    const query = document.getElementById('search-input');
    if (!query) return;

    const searchTerm = query.value.trim();
    console.log('🔍 Searching for:', searchTerm);

    if (!searchTerm) {
        loadProducts();
        return;
    }

    const tbody = document.getElementById('products-table-body');
    if (tbody) {
        tbody.innerHTML = '<tr><td colspan="8" class="empty-state"><div class="icon">⏳</div><p>Searching...</p></td></tr>';
    }

    try {
        const response = await fetch(`/api/products/search?q=${encodeURIComponent(searchTerm)}`);
        if (!response.ok) throw new Error('Search failed');
        const products = await response.json();
        console.log('🔍 Search results:', products.length);
        displayProducts(products);
    } catch (error) {
        console.error('❌ Search error:', error);
        alert('❌ Search failed. Please try again.');
    }
}

// Refresh products
function refreshProducts() {
    console.log('🔄 Refreshing products...');
    const searchInput = document.getElementById('search-input');
    if (searchInput) {
        searchInput.value = '';
    }
    loadProducts();
}

// Delete product
async function deleteProduct(id) {
    if (!confirm(`Are you sure you want to delete product #${id}?`)) return;

    console.log('🗑️ Deleting product:', id);

    try {
        const response = await fetch(`/api/products/${id}`, {
            method: 'DELETE'
        });
        const data = await response.json();

        if (data.success) {
            alert('✅ Product deleted successfully!');
            loadProducts();
        } else {
            alert('❌ Failed to delete product: ' + (data.message || 'Unknown error'));
        }
    } catch (error) {
        console.error('❌ Delete error:', error);
        alert('❌ Error deleting product. Please try again.');
    }
}

// ============================================
// SUPPLIERS PAGE FUNCTIONS
// ============================================

// Load all suppliers
async function loadSuppliers() {
    console.log('🏢 Loading suppliers...');
    const tbody = document.getElementById('suppliers-table-body');
    if (tbody) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-state"><div class="icon">⏳</div><p>Loading suppliers...</p></td></tr>';
    }

    try {
        const response = await fetch('/api/suppliers');
        if (!response.ok) throw new Error('Failed to fetch suppliers');
        const suppliers = await response.json();
        console.log('🏢 Suppliers loaded:', suppliers.length);
        displaySuppliers(suppliers);
    } catch (error) {
        console.error('❌ Error loading suppliers:', error);
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="6" class="empty-state"><div class="icon">❌</div><p>Error loading suppliers</p></td></tr>';
        }
    }
}

// Display suppliers in table
function displaySuppliers(suppliers) {
    const tbody = document.getElementById('suppliers-table-body');
    if (!tbody) return;

    if (!suppliers || suppliers.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="empty-state">
                    <div class="icon">🏢</div>
                    <p>No suppliers found. Add your first supplier!</p>
                </td>
            </tr>
        `;
        return;
    }

    let html = '';
    suppliers.forEach(s => {
        html += `
            <tr>
                <td>#${s.id}</td>
                <td><strong>${escapeHtml(s.name)}</strong></td>
                <td>${escapeHtml(s.contact_person || '-')}</td>
                <td>${escapeHtml(s.email || '-')}</td>
                <td>${escapeHtml(s.phone || '-')}</td>
                <td>
                    <button class="btn btn-danger btn-sm" onclick="deleteSupplier(${s.id})">Delete</button>
                </td>
            </tr>
        `;
    });

    tbody.innerHTML = html;
}

// Delete supplier
async function deleteSupplier(id) {
    if (!confirm(`Are you sure you want to delete supplier #${id}?`)) return;

    console.log('🗑️ Deleting supplier:', id);

    try {
        const response = await fetch(`/api/suppliers/${id}`, {
            method: 'DELETE'
        });
        const data = await response.json();

        if (data.success) {
            alert('✅ Supplier deleted successfully!');
            loadSuppliers();
        } else {
            alert('❌ Failed to delete supplier: ' + (data.message || 'Unknown error'));
        }
    } catch (error) {
        console.error('❌ Delete error:', error);
        alert('❌ Error deleting supplier. Please try again.');
    }
}

// ============================================
// DASHBOARD FUNCTIONS
// ============================================

// Load dashboard stats
async function loadDashboardStats() {
    console.log('📊 Loading dashboard stats...');

    try {
        const response = await fetch('/api/dashboard-stats');
        if (!response.ok) throw new Error('Failed to fetch stats');
        const stats = await response.json();
        console.log('📊 Stats loaded:', stats);
        displayStats(stats);
    } catch (error) {
        console.error('❌ Error loading stats:', error);
    }
}

// Display dashboard stats
function displayStats(stats) {
    const elements = {
        'total-products': stats.total_products || 0,
        'total-suppliers': stats.total_suppliers || 0,
        'low-stock': stats.low_stock || 0,
        'today-sales': '₹' + (stats.today_sales || 0).toLocaleString(),
        'total-sales': '₹' + (stats.total_sales || 0).toLocaleString()
    };

    for (const [id, value] of Object.entries(elements)) {
        const el = document.getElementById(id);
        if (el) {
            el.textContent = value;
        }
    }
}

// ============================================
// SALES REPORT FUNCTIONS
// ============================================

// Load sales report
async function loadSalesReport() {
    console.log('📈 Loading sales report...');
    const tbody = document.getElementById('sales-table-body');
    if (tbody) {
        tbody.innerHTML = '<tr><td colspan="6" class="empty-state"><div class="icon">⏳</div><p>Loading sales data...</p></td></tr>';
    }

    try {
        const startDate = document.getElementById('start-date');
        const endDate = document.getElementById('end-date');
        let url = '/api/sales-report';
        if (startDate && endDate && startDate.value && endDate.value) {
            url += `?start_date=${startDate.value}&end_date=${endDate.value}`;
        }

        const response = await fetch(url);
        if (!response.ok) throw new Error('Failed to fetch sales');
        const sales = await response.json();
        console.log('📈 Sales loaded:', sales.length);
        displaySales(sales);
    } catch (error) {
        console.error('❌ Error loading sales:', error);
        if (tbody) {
            tbody.innerHTML = '<tr><td colspan="6" class="empty-state"><div class="icon">❌</div><p>Error loading sales data</p></td></tr>';
        }
    }
}

// Display sales in table
function displaySales(sales) {
    const tbody = document.getElementById('sales-table-body');
    if (!tbody) return;

    if (!sales || sales.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="empty-state">
                    <div class="icon">📊</div>
                    <p>No sales records found.</p>
                </td>
            </tr>
        `;
        return;
    }

    let totalRevenue = 0;
    let totalItems = 0;
    let html = '';

    sales.forEach(s => {
        totalRevenue += s.total_price || 0;
        totalItems += s.quantity || 0;
        const date = s.sale_date ? new Date(s.sale_date).toLocaleDateString() : '-';

        html += `
            <tr>
                <td>#${s.id}</td>
                <td>${escapeHtml(s.product_name || '-')}</td>
                <td>${s.quantity}</td>
                <td>₹${(s.total_price || 0).toFixed(2)}</td>
                <td>${escapeHtml(s.customer_name || '-')}</td>
                <td>${date}</td>
            </tr>
        `;
    });

    tbody.innerHTML = html;

    // Update stats
    const totalSalesEl = document.getElementById('total-sales-count');
    const totalRevenueEl = document.getElementById('total-revenue');
    const totalItemsEl = document.getElementById('total-items');

    if (totalSalesEl) totalSalesEl.textContent = sales.length;
    if (totalRevenueEl) totalRevenueEl.textContent = '₹' + totalRevenue.toFixed(2);
    if (totalItemsEl) totalItemsEl.textContent = totalItems;
}

// Reset sales filter
function resetSalesFilter() {
    const startDate = document.getElementById('start-date');
    const endDate = document.getElementById('end-date');
    if (startDate) startDate.value = '';
    if (endDate) endDate.value = '';
    loadSalesReport();
}

// ============================================
// ADD PRODUCT PAGE FUNCTIONS
// ============================================

// Load suppliers for dropdown
async function loadSupplierDropdown() {
    console.log('📋 Loading suppliers for dropdown...');
    const select = document.getElementById('product-supplier');
    if (!select) return;

    try {
        const response = await fetch('/api/suppliers');
        if (!response.ok) throw new Error('Failed to fetch suppliers');
        const suppliers = await response.json();
        console.log('📋 Suppliers loaded for dropdown:', suppliers.length);

        select.innerHTML = '<option value="">Select Supplier</option>';
        suppliers.forEach(s => {
            const option = document.createElement('option');
            option.value = s.id;
            option.textContent = s.name;
            select.appendChild(option);
        });
    } catch (error) {
        console.error('❌ Error loading suppliers:', error);
    }
}

// Add product form submit
async function addProduct(event) {
    event.preventDefault();
    console.log('📦 Adding product...');

    const name = document.getElementById('product-name');
    const category = document.getElementById('product-category');
    const quantity = document.getElementById('product-quantity');
    const price = document.getElementById('product-price');
    const supplier = document.getElementById('product-supplier');
    const reorder = document.getElementById('product-reorder');
    const description = document.getElementById('product-description');

    const data = {
        name: name ? name.value.trim() : '',
        category: category ? category.value.trim() : '',
        quantity: quantity ? parseInt(quantity.value) || 0 : 0,
        price: price ? parseFloat(price.value) || 0 : 0,
        supplier_id: supplier ? parseInt(supplier.value) || 0 : 0,
        reorder_level: reorder ? parseInt(reorder.value) || 5 : 5,
        description: description ? description.value.trim() : ''
    };

    console.log('📦 Product data:', data);

    const successDiv = document.getElementById('success-msg');
    const errorDiv = document.getElementById('error-msg');
    if (successDiv) successDiv.style.display = 'none';
    if (errorDiv) errorDiv.style.display = 'none';

    try {
        const response = await fetch('/api/products', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        const result = await response.json();
        console.log('📦 Add product response:', result);

        if (result.success) {
            if (successDiv) {
                successDiv.textContent = '✅ Product added successfully!';
                successDiv.style.display = 'block';
            }
            // Reset form
            const form = document.getElementById('product-form');
            if (form) form.reset();
            setTimeout(() => {
                if (successDiv) successDiv.style.display = 'none';
            }, 3000);
        } else {
            if (errorDiv) {
                errorDiv.textContent = '❌ ' + (result.message || 'Failed to add product');
                errorDiv.style.display = 'block';
            }
        }
    } catch (error) {
        console.error('❌ Add product error:', error);
        if (errorDiv) {
            errorDiv.textContent = '❌ Network error. Please try again.';
            errorDiv.style.display = 'block';
        }
    }
}

// ============================================
// COMMON FUNCTIONS
// ============================================

// Escape HTML to prevent XSS
function escapeHtml(text) {
    if (!text) return '-';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Logout
async function logout() {
    if (!confirm('Are you sure you want to logout?')) return;

    console.log('🚪 Logging out...');

    try {
        await fetch('/api/logout', { method: 'POST' });
        window.location.href = '/login';
    } catch (error) {
        console.error('❌ Logout error:', error);
        window.location.href = '/login';
    }
}

// Toggle password visibility
function togglePassword(inputId, iconId) {
    const input = document.getElementById(inputId);
    const icon = document.getElementById(iconId);
    if (!input || !icon) return;

    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        input.type = 'password';
        icon.className = 'fas fa-eye';
    }
}

// ============================================
// PAGE INITIALIZATION
// ============================================

// Run when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM ready! Initializing page...');

    // Get current page URL
    const path = window.location.pathname;
    console.log('📍 Current page:', path);

    // ===== PRODUCTS PAGE =====
    if (path === '/products') {
        console.log('📦 Initializing Products page...');
        loadProducts();

        // Search button
        const searchBtn = document.getElementById('searchBtn');
        if (searchBtn) {
            searchBtn.addEventListener('click', searchProducts);
        }

        // Refresh button
        const refreshBtn = document.getElementById('refreshBtn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', refreshProducts);
        }

        // Enter key for search
        const searchInput = document.getElementById('search-input');
        if (searchInput) {
            searchInput.addEventListener('keyup', function(e) {
                if (e.key === 'Enter') {
                    searchProducts();
                }
            });
        }
    }

    // ===== ADD PRODUCT PAGE =====
    if (path === '/add-product') {
        console.log('📦 Initializing Add Product page...');
        loadSupplierDropdown();

        const form = document.getElementById('product-form');
        if (form) {
            form.addEventListener('submit', addProduct);
        }
    }

    // ===== DASHBOARD =====
    if (path === '/dashboard') {
        console.log('📊 Initializing Dashboard...');
        loadDashboardStats();

        // Refresh stats every 30 seconds
        setInterval(loadDashboardStats, 30000);
    }

    // ===== SUPPLIERS PAGE =====
    if (path === '/suppliers') {
        console.log('🏢 Initializing Suppliers page...');
        loadSuppliers();

        // Add supplier form
        const form = document.getElementById('supplier-form');
        if (form) {
            form.addEventListener('submit', async function(e) {
                e.preventDefault();
                console.log('🏢 Adding supplier...');

                const name = document.getElementById('supplier-name');
                const contact = document.getElementById('supplier-contact');
                const email = document.getElementById('supplier-email');
                const phone = document.getElementById('supplier-phone');
                const address = document.getElementById('supplier-address');

                const data = {
                    name: name ? name.value.trim() : '',
                    contact_person: contact ? contact.value.trim() : '',
                    email: email ? email.value.trim() : '',
                    phone: phone ? phone.value.trim() : '',
                    address: address ? address.value.trim() : ''
                };

                try {
                    const response = await fetch('/api/suppliers', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    const result = await response.json();

                    if (result.success) {
                        alert('✅ Supplier added successfully!');
                        closeModal();
                        loadSuppliers();
                        if (form) form.reset();
                    } else {
                        alert('❌ Failed to add supplier: ' + (result.message || 'Unknown error'));
                    }
                } catch (error) {
                    console.error('❌ Error:', error);
                    alert('❌ Error adding supplier. Please try again.');
                }
            });
        }
    }

    // ===== SALES REPORT =====
    if (path === '/sales-report') {
        console.log('📈 Initializing Sales Report...');
        loadSalesReport();

        // Filter button
        const filterBtn = document.getElementById('filterBtn');
        if (filterBtn) {
            filterBtn.addEventListener('click', loadSalesReport);
        }

        // Reset button
        const resetBtn = document.getElementById('resetBtn');
        if (resetBtn) {
            resetBtn.addEventListener('click', resetSalesFilter);
        }
    }

    // ===== LOGIN PAGE =====
    if (path === '/login') {
        console.log('🔐 Initializing Login page...');
        const form = document.getElementById('login-form');
        if (form) {
            form.addEventListener('submit', async function(e) {
                e.preventDefault();
                console.log('🔐 Logging in...');

                const username = document.getElementById('login-username');
                const password = document.getElementById('login-password');
                const errorDiv = document.getElementById('login-error');

                if (errorDiv) {
                    errorDiv.style.display = 'none';
                }

                try {
                    const response = await fetch('/api/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            username: username ? username.value.trim() : '',
                            password: password ? password.value : ''
                        })
                    });
                    const data = await response.json();
                    console.log('🔐 Login response:', data);

                    if (data.success) {
                        window.location.href = '/dashboard';
                    } else {
                        if (errorDiv) {
                            errorDiv.textContent = data.message || 'Invalid credentials';
                            errorDiv.style.display = 'block';
                        }
                    }
                } catch (error) {
                    console.error('❌ Login error:', error);
                    if (errorDiv) {
                        errorDiv.textContent = 'Network error. Please try again.';
                        errorDiv.style.display = 'block';
                    }
                }
            });
        }
    }

    // ===== SIGNUP PAGE =====
    if (path === '/signup') {
        console.log('📝 Initializing Signup page...');
        const form = document.getElementById('signup-form');
        if (form) {
            form.addEventListener('submit', async function(e) {
                e.preventDefault();
                console.log('📝 Signing up...');

                const fullName = document.getElementById('full-name');
                const username = document.getElementById('signup-username');
                const email = document.getElementById('signup-email');
                const password = document.getElementById('signup-password');
                const errorDiv = document.getElementById('signup-error');
                const successDiv = document.getElementById('signup-success');

                if (errorDiv) errorDiv.style.display = 'none';
                if (successDiv) successDiv.style.display = 'none';

                try {
                    const response = await fetch('/api/register', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            full_name: fullName ? fullName.value.trim() : '',
                            username: username ? username.value.trim() : '',
                            email: email ? email.value.trim() : '',
                            password: password ? password.value : ''
                        })
                    });
                    const data = await response.json();
                    console.log('📝 Signup response:', data);

                    if (data.success) {
                        if (successDiv) {
                            successDiv.textContent = '✅ Account created! Redirecting to login...';
                            successDiv.style.display = 'block';
                        }
                        setTimeout(() => {
                            window.location.href = '/login';
                        }, 2000);
                    } else {
                        if (errorDiv) {
                            errorDiv.textContent = data.message || 'Registration failed';
                            errorDiv.style.display = 'block';
                        }
                    }
                } catch (error) {
                    console.error('❌ Signup error:', error);
                    if (errorDiv) {
                        errorDiv.textContent = 'Network error. Please try again.';
                        errorDiv.style.display = 'block';
                    }
                }
            });
        }
    }

    console.log('✅ Page initialization complete!');
});

console.log('✅ Script loaded successfully!');