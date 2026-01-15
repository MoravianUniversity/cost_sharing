const TOKEN_KEY = 'cost_sharing_token';
const API_BASE = '';

let currentToken = null;
let currentUser = null;
let currentGroup = null;

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

                // Store user info from callback
                if (data.user) {
                    currentUser = data.user;
                }

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
            currentUser = user;
            displayUserInNav(user);
            fetchGroups();
        })
        .catch(error => {
            console.error('Error:', error);
            showError(error.message || 'Failed to fetch user info');
        });
}

function logout() {
    localStorage.removeItem(TOKEN_KEY);
    currentToken = null;
    currentUser = null;
    showLoggedOutState();
}

function displayUserInNav(user) {
    const navUserName = document.getElementById('nav-user-name');
    if (navUserName) {
        navUserName.textContent = user.name;
    }
}

function fetchGroups() {
    if (!currentToken) {
        return;
    }

    fetch(`${API_BASE}/groups`, {
        headers: {
            'Authorization': `Bearer ${currentToken}`
        }
    })
        .then(response => {
            if (!response.ok) {
                if (response.status === 401) {
                    logout();
                    throw new Error('Authentication failed');
                }
                return response.json().then(data => {
                    throw new Error(data.message || 'Failed to fetch groups');
                });
            }
            return response.json();
        })
        .then(data => {
            renderGroupsList(data.groups || []);
        })
        .catch(error => {
            console.error('Error:', error);
            showError(error.message || 'Failed to fetch groups');
        });
}

function renderGroupsList(groups) {
    const groupsListContainer = document.getElementById('groups-list');
    if (!groupsListContainer) {
        return;
    }

    if (groups.length === 0) {
        groupsListContainer.innerHTML = '<p>You are not a member of any groups yet.</p>';
        return;
    }

    groupsListContainer.innerHTML = groups.map(group => {
        const memberNames = (group.members || []).map(member => escapeHtml(member.name)).join(', ');
        return `
        <div class="group-card" onclick="viewGroupDetails(${group.id})" style="cursor: pointer;">
            <div class="group-card-header">
                <div>
                    <h3>${escapeHtml(group.name)}</h3>
                    <p class="group-description">${escapeHtml(group.description || '')}</p>
                    <div class="group-meta">Members: ${memberNames || 'None'}</div>
                </div>
                <div class="group-card-actions">
                    <button class="danger small" onclick="event.stopPropagation(); handleDeleteGroup(${group.id})">Delete</button>
                </div>
            </div>
        </div>
    `;
    }).join('');
}

function handleCreateGroup() {
    showCreateGroupModal();
}

function showCreateGroupModal() {
    // Create modal if it doesn't exist
    let modalOverlay = document.getElementById('create-group-modal');
    if (!modalOverlay) {
        modalOverlay = document.createElement('div');
        modalOverlay.id = 'create-group-modal';
        modalOverlay.className = 'modal-overlay';
        modalOverlay.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h2>Create New Group</h2>
                    <button class="modal-close" onclick="closeCreateGroupModal()">&times;</button>
                </div>
                <form id="create-group-form" onsubmit="submitCreateGroup(event)">
                    <div class="form-group">
                        <label for="group-name">Group Name <span class="required">*</span></label>
                        <input type="text" id="group-name" name="name" required maxlength="100" placeholder="Enter group name">
                    </div>
                    <div class="form-group">
                        <label for="group-description">Description</label>
                        <textarea id="group-description" name="description" maxlength="500" placeholder="Enter group description (optional)"></textarea>
                    </div>
                    <div class="form-actions">
                        <button type="button" class="secondary" onclick="closeCreateGroupModal()">Cancel</button>
                        <button type="submit">Create Group</button>
                    </div>
                </form>
            </div>
        `;
        document.body.appendChild(modalOverlay);
        
        // Close modal when clicking outside
        modalOverlay.addEventListener('click', function(event) {
            if (event.target === modalOverlay) {
                closeCreateGroupModal();
            }
        });
    }
    modalOverlay.classList.add('active');
    document.getElementById('group-name').focus();
}

function closeCreateGroupModal() {
    const modalOverlay = document.getElementById('create-group-modal');
    if (modalOverlay) {
        modalOverlay.classList.remove('active');
        document.getElementById('create-group-form').reset();
    }
}

function submitCreateGroup(event) {
    event.preventDefault();
    
    if (!currentToken) {
        showError('You must be logged in to create a group');
        return;
    }

    const form = event.target;
    const formData = new FormData(form);
    const name = formData.get('name').trim();
    const description = formData.get('description').trim();

    // Validate name
    if (!name || name.length === 0) {
        showError('Group name is required');
        return;
    }

    if (name.length > 100) {
        showError('Group name must be at most 100 characters');
        return;
    }

    if (description.length > 500) {
        showError('Description must be at most 500 characters');
        return;
    }

    // Prepare request body
    const requestBody = {
        name: name
    };
    if (description) {
        requestBody.description = description;
    }

    // Disable form during submission
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.textContent = 'Creating...';

    fetch(`${API_BASE}/groups`, {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${currentToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.message || 'Failed to create group');
                });
            }
            return response.json();
        })
        .then(data => {
            closeCreateGroupModal();
            // Refresh groups list
            fetchGroups();
        })
        .catch(error => {
            console.error('Error:', error);
            showError(error.message || 'Failed to create group');
        })
        .finally(() => {
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        });
}

function handleDeleteGroup(groupId) {
    alert('Not implemented');
}

function viewGroupDetails(groupId) {
    fetchGroupDetails(groupId);
}

function fetchGroupDetails(groupId) {
    if (!currentToken) {
        showError('You must be logged in to view group details');
        return;
    }

    fetch(`${API_BASE}/groups/${groupId}`, {
        headers: {
            'Authorization': `Bearer ${currentToken}`
        }
    })
        .then(response => {
            if (!response.ok) {
                if (response.status === 401) {
                    logout();
                    throw new Error('Authentication failed');
                }
                if (response.status === 403) {
                    throw new Error('You do not have access to this group');
                }
                if (response.status === 404) {
                    throw new Error('Group not found');
                }
                return response.json().then(data => {
                    throw new Error(data.message || 'Failed to fetch group details');
                });
            }
            return response.json();
        })
        .then(group => {
            currentGroup = group;
            renderGroupDetails(group);
            showGroupDetailsView();
        })
        .catch(error => {
            console.error('Error:', error);
            showError(error.message || 'Failed to fetch group details');
        });
}

function renderGroupDetails(group) {
    // Update group header
    document.getElementById('group-details-name').textContent = group.name || '';
    const descriptionEl = document.getElementById('group-details-description');
    if (group.description) {
        descriptionEl.textContent = group.description;
        descriptionEl.style.display = 'block';
    } else {
        descriptionEl.textContent = '';
        descriptionEl.style.display = 'none';
    }

    // Render members
    renderGroupMembers(group.members || [], group.createdBy || null);
}

function renderGroupMembers(members, creator) {
    const membersContainer = document.getElementById('group-details-members');
    if (!membersContainer) {
        return;
    }

    if (members.length === 0) {
        membersContainer.innerHTML = '<p>No members in this group.</p>';
        return;
    }

    const creatorId = creator ? creator.id : null;

    membersContainer.innerHTML = members.map(member => {
        const isCreator = creatorId && member.id === creatorId;
        const creatorBadge = isCreator ? '<span class="member-badge">Creator</span>' : '';
        
        return `
            <div class="member-item">
                <div class="member-info">
                    <div class="member-name">${escapeHtml(member.name)} ${creatorBadge}</div>
                    <div class="member-email">${escapeHtml(member.email)}</div>
                </div>
            </div>
        `;
    }).join('');
}

function showGroupDetailsView() {
    document.getElementById('groups-list-view').classList.add('hidden');
    document.getElementById('group-details-view').classList.remove('hidden');
}

function showGroupsList() {
    document.getElementById('group-details-view').classList.add('hidden');
    document.getElementById('groups-list-view').classList.remove('hidden');
    currentGroup = null;
}

function switchTab(tabName) {
    // Remove active class from all tabs and tab contents
    document.querySelectorAll('.tab').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });

    // Add active class to selected tab
    const tabButton = Array.from(document.querySelectorAll('.tab')).find(btn => {
        return btn.textContent.trim().toLowerCase() === tabName.toLowerCase();
    });
    if (tabButton) {
        tabButton.classList.add('active');
    }

    // Show selected tab content
    const tabContent = document.getElementById(`tab-${tabName}`);
    if (tabContent) {
        tabContent.classList.add('active');
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function showLoggedInState() {
    document.getElementById('navigation').classList.remove('hidden');
    document.getElementById('login-section').classList.add('hidden');
    document.getElementById('groups-section').classList.remove('hidden');
    // Ensure we show groups list view by default
    showGroupsList();
}

function showLoggedOutState() {
    document.getElementById('navigation').classList.add('hidden');
    document.getElementById('login-section').classList.remove('hidden');
    document.getElementById('groups-section').classList.add('hidden');
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

