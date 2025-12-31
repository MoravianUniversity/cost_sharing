const TOKEN_KEY = 'cost_sharing_token';
const API_BASE = '';

let currentToken = null;

function init() {
    // Check for token in localStorage
    currentToken = localStorage.getItem(TOKEN_KEY);

    // Check if we're handling an OAuth callback
    const urlParams = new URLSearchParams(window.location.search);
    const code = urlParams.get('code');

    if (code) {
        handleCallback(code);
    } else if (currentToken) {
        showLoggedInState();
        fetchUserInfo();
    } else {
        showLoggedOutState();
    }
}

function handleCallback(code) {
    fetch(`${API_BASE}/auth/callback?code=${encodeURIComponent(code)}`)
        .then(response => response.json())
        .then(data => {
            if (data.token) {
                // Store token
                localStorage.setItem(TOKEN_KEY, data.token);
                currentToken = data.token;

                // Clean URL (remove query params)
                window.history.replaceState({}, document.title, window.location.pathname);

                // Show logged in state
                showLoggedInState();
                fetchUserInfo();
            } else {
                showError(data.message || 'Authentication failed');
                showLoggedOutState();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('Failed to complete authentication');
            showLoggedOutState();
        });
}

function login() {
    fetch(`${API_BASE}/auth/login`)
        .then(response => response.json())
        .then(data => {
            if (data.url) {
                // Redirect to Google OAuth
                window.location.href = data.url;
            } else {
                showError('Failed to get login URL');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showError('Failed to initiate login');
        });
}

function fetchUserInfo() {
    if (!currentToken) {
        return;
    }

    fetch(`${API_BASE}/auth/me`, {
        headers: {
            'Authorization': `Bearer ${currentToken}`
        }
    })
        .then(response => {
            if (!response.ok) {
                if (response.status === 401) {
                    // Token invalid, clear it
                    logout();
                    throw new Error('Authentication failed');
                }
                return response.json().then(data => {
                    throw new Error(data.message || 'Failed to fetch user info');
                });
            }
            return response.json();
        })
        .then(user => {
            displayUserInfo(user);
        })
        .catch(error => {
            console.error('Error:', error);
            showError(error.message || 'Failed to fetch user info');
        });
}

function logout() {
    localStorage.removeItem(TOKEN_KEY);
    currentToken = null;
    showLoggedOutState();
}

function displayUserInfo(user) {
    document.getElementById('user-id').textContent = user.id;
    document.getElementById('user-email').textContent = user.email;
    document.getElementById('user-name').textContent = user.name;
    document.getElementById('user-token').textContent = currentToken;
}

function showLoggedInState() {
    document.getElementById('status').textContent = '✓ Logged In';
    document.getElementById('status').className = 'status logged-in';
    document.getElementById('login-section').classList.add('hidden');
    document.getElementById('user-section').classList.remove('hidden');
}

function showLoggedOutState() {
    document.getElementById('status').textContent = 'Not Logged In';
    document.getElementById('status').className = 'status logged-out';
    document.getElementById('login-section').classList.remove('hidden');
    document.getElementById('user-section').classList.add('hidden');
}

function showError(message) {
    let errorDiv = document.getElementById('error');
    if (!errorDiv) {
        errorDiv = document.createElement('div');
        errorDiv.id = 'error';
        errorDiv.className = 'error';
        document.querySelector('.container').insertBefore(errorDiv, document.querySelector('.container').firstChild);
    }
    errorDiv.textContent = message;
    errorDiv.classList.remove('hidden');

    // Hide error after 5 seconds
    setTimeout(() => {
        errorDiv.classList.add('hidden');
    }, 5000);
}

// Initialize when DOM is loaded
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

