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

    // Show "Add Member" button (all members can add other members)
    const addMemberButton = document.getElementById('group-details-add-member');
    if (addMemberButton) {
        addMemberButton.style.display = 'block';
    }

    // Show "Add Expense" button (all members can add expenses)
    const addExpenseButton = document.getElementById('group-details-add-expense');
    if (addExpenseButton) {
        addExpenseButton.style.display = 'block';
    }

    // Render members
    renderGroupMembers(group.members || [], group.createdBy || null);
    
    // If expenses tab is active, fetch expenses
    const expensesTab = document.getElementById('tab-expenses');
    if (expensesTab && expensesTab.classList.contains('active')) {
        fetchGroupExpenses(group.id);
    }
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

function handleAddMember() {
    if (!currentGroup) {
        showError('No group selected');
        return;
    }
    showAddMemberModal();
}

function handleAddExpense() {
    if (!currentGroup) {
        showError('No group selected');
        return;
    }
    if (!currentUser) {
        showError('You must be logged in to add an expense');
        return;
    }
    showAddExpenseModal();
}

function showAddExpenseModal() {
    if (!currentGroup || !currentUser) {
        return;
    }

    // Create modal if it doesn't exist
    let modalOverlay = document.getElementById('add-expense-modal');
    if (!modalOverlay) {
        modalOverlay = document.createElement('div');
        modalOverlay.id = 'add-expense-modal';
        modalOverlay.className = 'modal-overlay';
        modalOverlay.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h2>Create Expense</h2>
                    <button class="modal-close" onclick="closeAddExpenseModal()">&times;</button>
                </div>
                <p>You (${escapeHtml(currentUser.name)}) will be recorded as the person who paid for this expense.</p>
                <form id="add-expense-form" onsubmit="submitAddExpense(event)">
                    <div class="form-group">
                        <label for="expense-description">Description <span class="required">*</span></label>
                        <input type="text" id="expense-description" name="description" required 
                               placeholder="e.g., Grocery shopping" maxlength="200">
                        <small class="form-help">Required. 1-200 characters.</small>
                    </div>
                    <div class="form-group">
                        <label for="expense-amount">Amount ($) <span class="required">*</span></label>
                        <input type="number" id="expense-amount" name="amount" step="0.01" min="0.01" 
                               placeholder="0.00" required>
                        <small class="form-help">Required. Minimum $0.01.</small>
                    </div>
                    <div class="form-group">
                        <label for="expense-date">Date <span class="required">*</span></label>
                        <input type="date" id="expense-date" name="date" required>
                        <small class="form-help">Required. Date when the expense occurred.</small>
                    </div>
                    <div class="form-group">
                        <label>Split between (select all who should share this expense) <span class="required">*</span></label>
                        <div class="checkbox-group" id="expense-split-between">
                            <!-- Checkboxes will be dynamically inserted here -->
                        </div>
                        <small class="form-help">Required. You must be included. Select all group members who should share this expense.</small>
                    </div>
                    <div class="form-actions">
                        <button type="button" class="secondary" onclick="closeAddExpenseModal()">Cancel</button>
                        <button type="submit">Create Expense</button>
                    </div>
                </form>
            </div>
        `;
        document.body.appendChild(modalOverlay);
        
        // Close modal when clicking outside
        modalOverlay.addEventListener('click', function(event) {
            if (event.target === modalOverlay) {
                closeAddExpenseModal();
            }
        });
    }

    // Populate checkboxes with group members (always refresh in case members changed)
    const checkboxGroup = document.getElementById('expense-split-between');
    if (checkboxGroup && currentGroup.members) {
        checkboxGroup.innerHTML = currentGroup.members.map(member => {
            const isCurrentUser = member.id === currentUser.id;
            return `
                <div class="checkbox-item">
                    <input type="checkbox" id="split-${member.id}" value="${member.id}" 
                           ${isCurrentUser ? 'checked disabled' : ''}>
                    <label for="split-${member.id}" ${isCurrentUser ? 'style="color: #6c757d;"' : ''}>
                        ${escapeHtml(member.name)} (${escapeHtml(member.email)})${isCurrentUser ? ' (payer)' : ''}
                    </label>
                </div>
            `;
        }).join('');
    }

    // Set today's date as default (always set when opening modal)
    const dateInput = document.getElementById('expense-date');
    if (dateInput) {
        const today = new Date().toISOString().split('T')[0];
        dateInput.value = today;
    }

    modalOverlay.classList.add('active');
    const descriptionInput = document.getElementById('expense-description');
    if (descriptionInput) {
        descriptionInput.focus();
    }
}

function closeAddExpenseModal() {
    const modalOverlay = document.getElementById('add-expense-modal');
    if (modalOverlay) {
        modalOverlay.classList.remove('active');
        const form = document.getElementById('add-expense-form');
        if (form) {
            form.reset();
        }
        // Clear any validation errors
        clearFormErrors('add-expense-form');
    }
}

function submitAddExpense(event) {
    event.preventDefault();
    
    if (!currentToken) {
        showError('You must be logged in to create an expense');
        return;
    }

    if (!currentGroup) {
        showError('No group selected');
        return;
    }

    if (!currentUser) {
        showError('User information not available');
        return;
    }

    const form = event.target;
    const formData = new FormData(form);
    const description = formData.get('description').trim();
    const amount = parseFloat(formData.get('amount'));
    const date = formData.get('date');

    // Clear previous errors
    clearFormErrors('add-expense-form');

    // Validate description
    if (!description || description.length === 0) {
        showFormError('expense-description', 'Description is required');
        return;
    }
    if (description.length > 200) {
        showFormError('expense-description', 'Description must be at most 200 characters');
        return;
    }

    // Validate amount
    if (!amount || isNaN(amount)) {
        showFormError('expense-amount', 'Amount is required');
        return;
    }
    if (amount < 0.01) {
        showFormError('expense-amount', 'Amount must be at least $0.01');
        return;
    }

    // Validate date
    if (!date) {
        showFormError('expense-date', 'Date is required');
        return;
    }
    // Validate date format (YYYY-MM-DD)
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(date)) {
        showFormError('expense-date', 'Date must be in YYYY-MM-DD format');
        return;
    }

    // Get selected users for splitBetween
    const checkboxes = document.querySelectorAll('#expense-split-between input[type="checkbox"]:checked');
    const splitBetween = Array.from(checkboxes).map(cb => parseInt(cb.value));

    // Validate splitBetween
    if (splitBetween.length === 0) {
        showError('You must select at least one person to split the expense with');
        return;
    }

    // Validate current user is included (should always be true since checkbox is checked and disabled)
    if (!splitBetween.includes(currentUser.id)) {
        showError('You must be included in the expense split');
        return;
    }

    // Validate all selected users are group members (client-side validation)
    if (currentGroup.members) {
        const memberIds = currentGroup.members.map(m => m.id);
        const invalidUsers = splitBetween.filter(userId => !memberIds.includes(userId));
        if (invalidUsers.length > 0) {
            showError('All selected users must be members of this group');
            return;
        }
    }

    // Prepare request body
    const requestBody = {
        description: description,
        amount: amount,
        date: date,
        splitBetween: splitBetween
    };

    // Disable form during submission
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.textContent = 'Creating...';

    fetch(`${API_BASE}/groups/${currentGroup.id}/expenses`, {
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
                    throw new Error(data.message || 'Failed to create expense');
                });
            }
            return response.json();
        })
        .then(expense => {
            closeAddExpenseModal();
            // Switch to Expenses tab
            switchTab('expenses');
            // Reload expenses data
            fetchGroupExpenses(currentGroup.id);
        })
        .catch(error => {
            console.error('Error:', error);
            showError(error.message || 'Failed to create expense');
        })
        .finally(() => {
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        });
}

function showAddMemberModal() {
    // Create modal if it doesn't exist
    let modalOverlay = document.getElementById('add-member-modal');
    if (!modalOverlay) {
        modalOverlay = document.createElement('div');
        modalOverlay.id = 'add-member-modal';
        modalOverlay.className = 'modal-overlay';
        modalOverlay.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h2>Add Member</h2>
                    <button class="modal-close" onclick="closeAddMemberModal()">&times;</button>
                </div>
                <form id="add-member-form" onsubmit="submitAddMember(event)">
                    <div class="form-group">
                        <label for="member-email">Email <span class="required">*</span></label>
                        <input type="email" id="member-email" name="email" required placeholder="user@example.com">
                        <small class="form-help">Required. A user account will be created if it doesn't exist.</small>
                    </div>
                    <div class="form-group">
                        <label for="member-name">Name <span class="required">*</span></label>
                        <input type="text" id="member-name" name="name" required placeholder="Full Name">
                        <small class="form-help">Required. The member's full name.</small>
                    </div>
                    <div class="form-actions">
                        <button type="button" class="secondary" onclick="closeAddMemberModal()">Cancel</button>
                        <button type="submit">Add Member</button>
                    </div>
                </form>
            </div>
        `;
        document.body.appendChild(modalOverlay);
        
        // Close modal when clicking outside
        modalOverlay.addEventListener('click', function(event) {
            if (event.target === modalOverlay) {
                closeAddMemberModal();
            }
        });
    }
    modalOverlay.classList.add('active');
    document.getElementById('member-email').focus();
}

function closeAddMemberModal() {
    const modalOverlay = document.getElementById('add-member-modal');
    if (modalOverlay) {
        modalOverlay.classList.remove('active');
        const form = document.getElementById('add-member-form');
        if (form) {
            form.reset();
        }
        // Clear any validation errors
        clearFormErrors('add-member-form');
    }
}

function submitAddMember(event) {
    event.preventDefault();
    
    if (!currentToken) {
        showError('You must be logged in to add a member');
        return;
    }

    if (!currentGroup) {
        showError('No group selected');
        return;
    }

    const form = event.target;
    const formData = new FormData(form);
    const email = formData.get('email').trim();
    const name = formData.get('name').trim();

    // Clear previous errors
    clearFormErrors('add-member-form');

    // Validate email
    if (!email || email.length === 0) {
        showFormError('member-email', 'Email is required');
        return;
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        showFormError('member-email', 'Email must be a valid email address');
        return;
    }

    // Validate name
    if (!name || name.length === 0) {
        showFormError('member-name', 'Name is required');
        return;
    }

    // Check if email is already in the group (client-side validation to avoid 409)
    if (currentGroup && currentGroup.members) {
        const existingMember = currentGroup.members.find(member => 
            member.email.toLowerCase() === email.toLowerCase()
        );
        if (existingMember) {
            showFormError('member-email', 'This user is already a member of this group');
            return;
        }
    }

    // Prepare request body
    const requestBody = {
        email: email,
        name: name
    };

    // Disable form during submission
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.textContent = 'Adding...';

    fetch(`${API_BASE}/groups/${currentGroup.id}/members`, {
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
                    throw new Error(data.message || 'Failed to add member');
                });
            }
            return response.json();
        })
        .then(group => {
            // Update currentGroup with the returned group
            currentGroup = group;
            closeAddMemberModal();
            // Re-render group details with updated members
            renderGroupDetails(group);
        })
        .catch(error => {
            console.error('Error:', error);
            showError(error.message || 'Failed to add member');
        })
        .finally(() => {
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        });
}

function showFormError(fieldId, message) {
    const field = document.getElementById(fieldId);
    if (!field) {
        return;
    }

    // Remove existing error
    const existingError = field.parentElement.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }

    // Add error styling
    field.classList.add('field-error-input');
    
    // Add error message
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    field.parentElement.appendChild(errorDiv);
}

function clearFormErrors(formId) {
    const form = document.getElementById(formId);
    if (!form) {
        return;
    }

    // Remove all error styling and messages
    form.querySelectorAll('.field-error-input').forEach(field => {
        field.classList.remove('field-error-input');
    });
    form.querySelectorAll('.field-error').forEach(error => {
        error.remove();
    });
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

    // Fetch expenses when expenses tab is selected
    if (tabName === 'expenses' && currentGroup) {
        fetchGroupExpenses(currentGroup.id);
    }
}

function fetchGroupExpenses(groupId) {
    if (!currentToken) {
        showError('You must be logged in to view expenses');
        return;
    }

    if (!currentGroup) {
        showError('No group selected');
        return;
    }

    const expensesContainer = document.getElementById('expenses-container');
    if (!expensesContainer) {
        return;
    }

    // Show loading state
    expensesContainer.innerHTML = '<p style="color: #6c757d;">Loading expenses...</p>';

    fetch(`${API_BASE}/groups/${groupId}/expenses`, {
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
                    throw new Error(data.message || 'Failed to fetch expenses');
                });
            }
            return response.json();
        })
        .then(data => {
            renderExpenses(data.expenses || []);
        })
        .catch(error => {
            console.error('Error:', error);
            showError(error.message || 'Failed to fetch expenses');
            expensesContainer.innerHTML = '<p style="color: #dc3545;">Failed to load expenses.</p>';
        });
}

function renderExpenses(expenses) {
    const expensesContainer = document.getElementById('expenses-container');
    if (!expensesContainer) {
        return;
    }

    if (!currentUser) {
        expensesContainer.innerHTML = '<p style="color: #6c757d;">Unable to display expenses.</p>';
        return;
    }

    const currentUserId = currentUser.id;
    let totalUserShare = 0;

    if (expenses.length === 0) {
        expensesContainer.innerHTML = '<p style="color: #6c757d;">No expenses in this group yet.</p>';
        return;
    }

    // Calculate total user share
    expenses.forEach(expense => {
        const isParticipant = expense.splitBetween.some(user => user.id === currentUserId);
        if (isParticipant) {
            totalUserShare += expense.perPersonAmount || 0;
        }
    });

    // Format date helper
    function formatDate(dateString) {
        const date = new Date(dateString + 'T00:00:00');
        const months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
        return `${months[date.getMonth()]} ${date.getDate()}, ${date.getFullYear()}`;
    }

    // Format currency helper
    function formatCurrency(amount) {
        return `$${amount.toFixed(2)}`;
    }

    // Build expenses table
    const expensesHtml = `
        <table style="margin-top: 20px;">
            <thead>
                <tr>
                    <th>Expense</th>
                    <th style="text-align: center;">People</th>
                    <th style="text-align: right;">Total Amount</th>
                    <th style="text-align: right;">Your Share</th>
                    <th style="text-align: center;">Actions</th>
                </tr>
            </thead>
            <tbody>
                ${expenses.map(expense => {
                    const isParticipant = expense.splitBetween.some(user => user.id === currentUserId);
                    const isPayer = expense.paidBy.id === currentUserId;
                    const userShare = isParticipant ? (expense.perPersonAmount || 0) : 0;
                    
                    return `
                        <tr>
                            <td>
                                <div style="font-weight: 600; color: #333; margin-bottom: 5px;">${escapeHtml(expense.description)}</div>
                                <div style="font-size: 0.9em; color: #6c757d;">Paid by ${escapeHtml(expense.paidBy.name)} on ${formatDate(expense.date)}</div>
                            </td>
                            <td style="text-align: center;">
                                <div style="font-weight: 600; color: #495057;">${expense.splitBetween.length}</div>
                            </td>
                            <td style="text-align: right;">
                                <div class="expense-amount" style="margin: 0;">${formatCurrency(expense.amount)}</div>
                            </td>
                            <td style="text-align: right;">
                                ${isParticipant ? 
                                    `<div class="expense-amount" style="margin: 0; color: #28a745; font-weight: 600;">${formatCurrency(userShare)}</div>` :
                                    '<div style="color: #6c757d; font-size: 0.9em;">Not included</div>'
                                }
                            </td>
                            <td style="text-align: right;">
                                ${isPayer ? 
                                    `<div style="display: flex; gap: 10px; justify-content: flex-end;">
                                        <button class="small secondary" onclick="handleEditExpense(${expense.id}, ${expense.groupId})">Edit</button>
                                        <button class="small danger" onclick="handleDeleteExpense(${expense.id}, ${expense.groupId})">Delete</button>
                                    </div>` :
                                    ''
                                }
                            </td>
                        </tr>
                    `;
                }).join('')}
                <tr style="background-color: #f8f9fa; font-weight: 600;">
                    <td style="border-top: 2px solid #dee2e6; padding-top: 15px;">
                        <div>Your total share of expenses</div>
                        <div style="font-size: 0.9em; font-weight: normal; color: #6c757d; margin-top: 5px;">Sum of your share from all expenses</div>
                    </td>
                    <td style="border-top: 2px solid #dee2e6; padding-top: 15px;"></td>
                    <td style="text-align: right; border-top: 2px solid #dee2e6; padding-top: 15px;"></td>
                    <td style="text-align: right; border-top: 2px solid #dee2e6; padding-top: 15px;">
                        <div class="expense-amount" style="margin: 0; font-size: 1.2em; color: #28a745;">${formatCurrency(totalUserShare)}</div>
                    </td>
                    <td style="border-top: 2px solid #dee2e6; padding-top: 15px;"></td>
                </tr>
            </tbody>
        </table>
    `;

    expensesContainer.innerHTML = expensesHtml;
}

function handleEditExpense(expenseId, groupId) {
    if (!currentToken) {
        showError('You must be logged in to edit an expense');
        return;
    }
    fetchExpenseDetails(expenseId, groupId);
}

function fetchExpenseDetails(expenseId, groupId) {
    fetch(`${API_BASE}/groups/${groupId}/expenses/${expenseId}`, {
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
                    throw new Error('You do not have access to this expense');
                }
                if (response.status === 404) {
                    throw new Error('Expense not found');
                }
                return response.json().then(data => {
                    throw new Error(data.message || 'Failed to fetch expense details');
                });
            }
            return response.json();
        })
        .then(expense => {
            showEditExpenseModal(expense);
        })
        .catch(error => {
            console.error('Error:', error);
            showError(error.message || 'Failed to fetch expense details');
        });
}

function showEditExpenseModal(expense) {
    if (!currentGroup || !currentUser) {
        return;
    }

    // Create modal if it doesn't exist
    let modalOverlay = document.getElementById('edit-expense-modal');
    if (!modalOverlay) {
        modalOverlay = document.createElement('div');
        modalOverlay.id = 'edit-expense-modal';
        modalOverlay.className = 'modal-overlay';
        modalOverlay.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h2>Edit Expense</h2>
                    <button class="modal-close" onclick="closeEditExpenseModal()">&times;</button>
                </div>
                <p id="edit-expense-payer-message">You (${escapeHtml(currentUser.name)}) are recorded as the person who paid for this expense.</p>
                <form id="edit-expense-form" onsubmit="submitEditExpense(event)">
                    <div class="form-group">
                        <label for="edit-expense-description">Description <span class="required">*</span></label>
                        <input type="text" id="edit-expense-description" name="description" required 
                               placeholder="e.g., Grocery shopping" maxlength="200">
                        <small class="form-help">Required. 1-200 characters.</small>
                    </div>
                    <div class="form-group">
                        <label for="edit-expense-amount">Amount ($) <span class="required">*</span></label>
                        <input type="number" id="edit-expense-amount" name="amount" step="0.01" min="0.01" 
                               placeholder="0.00" required>
                        <small class="form-help">Required. Minimum $0.01.</small>
                    </div>
                    <div class="form-group">
                        <label for="edit-expense-date">Date <span class="required">*</span></label>
                        <input type="date" id="edit-expense-date" name="date" required>
                        <small class="form-help">Required. Date when the expense occurred.</small>
                    </div>
                    <div class="form-group">
                        <label>Split between (select all who should share this expense) <span class="required">*</span></label>
                        <div class="checkbox-group" id="edit-expense-split-between">
                            <!-- Checkboxes will be dynamically inserted here -->
                        </div>
                        <small class="form-help">Required. You must be included. Select all group members who should share this expense.</small>
                    </div>
                    <div class="form-actions">
                        <button type="button" class="secondary" onclick="closeEditExpenseModal()">Cancel</button>
                        <button type="submit">Update Expense</button>
                    </div>
                </form>
            </div>
        `;
        document.body.appendChild(modalOverlay);
        
        // Close modal when clicking outside
        modalOverlay.addEventListener('click', function(event) {
            if (event.target === modalOverlay) {
                closeEditExpenseModal();
            }
        });
    }

    // Populate form with expense data
    document.getElementById('edit-expense-description').value = expense.description || '';
    document.getElementById('edit-expense-amount').value = expense.amount || '';
    document.getElementById('edit-expense-date').value = expense.date || '';

    // Update payer message
    const payerMessage = document.getElementById('edit-expense-payer-message');
    if (payerMessage && expense.paidBy) {
        payerMessage.textContent = `You (${expense.paidBy.name}) are recorded as the person who paid for this expense.`;
    }

    // Populate checkboxes with group members
    const checkboxGroup = document.getElementById('edit-expense-split-between');
    if (checkboxGroup && currentGroup.members) {
        const participantIds = expense.splitBetween.map(p => p.id);
        checkboxGroup.innerHTML = currentGroup.members.map(member => {
            const isCurrentUser = member.id === currentUser.id;
            const isParticipant = participantIds.includes(member.id);
            return `
                <div class="checkbox-item">
                    <input type="checkbox" id="edit-split-${member.id}" value="${member.id}" 
                           ${isCurrentUser ? 'checked disabled' : (isParticipant ? 'checked' : '')}>
                    <label for="edit-split-${member.id}" ${isCurrentUser ? 'style="color: #6c757d;"' : ''}>
                        ${escapeHtml(member.name)} (${escapeHtml(member.email)})${isCurrentUser ? ' (payer)' : ''}
                    </label>
                </div>
            `;
        }).join('');
    }

    // Store expense ID and group ID for form submission
    modalOverlay.dataset.expenseId = expense.id;
    modalOverlay.dataset.groupId = expense.groupId;

    modalOverlay.classList.add('active');
    const descriptionInput = document.getElementById('edit-expense-description');
    if (descriptionInput) {
        descriptionInput.focus();
    }
}

function closeEditExpenseModal() {
    const modalOverlay = document.getElementById('edit-expense-modal');
    if (modalOverlay) {
        modalOverlay.classList.remove('active');
        const form = document.getElementById('edit-expense-form');
        if (form) {
            form.reset();
        }
        // Clear any validation errors
        clearFormErrors('edit-expense-form');
    }
}

function submitEditExpense(event) {
    event.preventDefault();
    
    if (!currentToken) {
        showError('You must be logged in to update an expense');
        return;
    }

    const modalOverlay = document.getElementById('edit-expense-modal');
    if (!modalOverlay) {
        return;
    }

    const expenseId = modalOverlay.dataset.expenseId;
    const groupId = modalOverlay.dataset.groupId;

    if (!expenseId || !groupId) {
        showError('Expense information not available');
        return;
    }

    if (!currentUser) {
        showError('User information not available');
        return;
    }

    const form = event.target;
    const formData = new FormData(form);
    const description = formData.get('description').trim();
    const amount = parseFloat(formData.get('amount'));
    const date = formData.get('date');

    // Clear previous errors
    clearFormErrors('edit-expense-form');

    // Validate description
    if (!description || description.length === 0) {
        showFormError('edit-expense-description', 'Description is required');
        return;
    }
    if (description.length > 200) {
        showFormError('edit-expense-description', 'Description must be at most 200 characters');
        return;
    }

    // Validate amount
    if (!amount || isNaN(amount)) {
        showFormError('edit-expense-amount', 'Amount is required');
        return;
    }
    if (amount < 0.01) {
        showFormError('edit-expense-amount', 'Amount must be at least $0.01');
        return;
    }

    // Validate date
    if (!date) {
        showFormError('edit-expense-date', 'Date is required');
        return;
    }
    // Validate date format (YYYY-MM-DD)
    const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
    if (!dateRegex.test(date)) {
        showFormError('edit-expense-date', 'Date must be in YYYY-MM-DD format');
        return;
    }

    // Get selected users for splitBetween
    const checkboxes = document.querySelectorAll('#edit-expense-split-between input[type="checkbox"]:checked');
    const splitBetween = Array.from(checkboxes).map(cb => parseInt(cb.value));

    // Validate splitBetween
    if (splitBetween.length === 0) {
        showError('You must select at least one person to split the expense with');
        return;
    }

    // Validate current user is included (should always be true since checkbox is checked and disabled)
    if (!splitBetween.includes(currentUser.id)) {
        showError('You must be included in the expense split');
        return;
    }

    // Validate all selected users are group members (client-side validation)
    if (currentGroup.members) {
        const memberIds = currentGroup.members.map(m => m.id);
        const invalidUsers = splitBetween.filter(userId => !memberIds.includes(userId));
        if (invalidUsers.length > 0) {
            showError('All selected users must be members of this group');
            return;
        }
    }

    // Prepare request body
    const requestBody = {
        description: description,
        amount: amount,
        date: date,
        splitBetween: splitBetween
    };

    // Disable form during submission
    const submitButton = form.querySelector('button[type="submit"]');
    const originalText = submitButton.textContent;
    submitButton.disabled = true;
    submitButton.textContent = 'Updating...';

    fetch(`${API_BASE}/groups/${groupId}/expenses/${expenseId}`, {
        method: 'PUT',
        headers: {
            'Authorization': `Bearer ${currentToken}`,
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestBody)
    })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.message || 'Failed to update expense');
                });
            }
            return response.json();
        })
        .then(expense => {
            closeEditExpenseModal();
            // Reload expenses data
            fetchGroupExpenses(groupId);
        })
        .catch(error => {
            console.error('Error:', error);
            showError(error.message || 'Failed to update expense');
        })
        .finally(() => {
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        });
}

function handleDeleteExpense(expenseId, groupId) {
    if (!currentToken) {
        showError('You must be logged in to delete an expense');
        return;
    }
    // Fetch expense details to show in confirmation dialog
    fetchExpenseDetailsForDelete(expenseId, groupId);
}

function fetchExpenseDetailsForDelete(expenseId, groupId) {
    fetch(`${API_BASE}/groups/${groupId}/expenses/${expenseId}`, {
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
                    throw new Error(data.message || 'Failed to fetch expense details');
                });
            }
            return response.json();
        })
        .then(expense => {
            showDeleteExpenseConfirmationModal(expense);
        })
        .catch(error => {
            console.error('Error:', error);
            showError(error.message || 'Failed to fetch expense details');
        });
}

function showDeleteExpenseConfirmationModal(expense) {
    // Create modal if it doesn't exist
    let modalOverlay = document.getElementById('delete-expense-modal');
    if (!modalOverlay) {
        modalOverlay = document.createElement('div');
        modalOverlay.id = 'delete-expense-modal';
        modalOverlay.className = 'modal-overlay';
        modalOverlay.innerHTML = `
            <div class="modal">
                <div class="modal-header">
                    <h2>Delete Expense</h2>
                    <button class="modal-close" onclick="closeDeleteExpenseModal()">&times;</button>
                </div>
                <p>Are you sure you want to delete this expense?</p>
                <p style="font-weight: 600; color: #333; margin: 10px 0;">"<span id="delete-expense-description"></span>"</p>
                <p style="color: #6c757d; font-size: 0.9em;">This action cannot be undone.</p>
                <div class="form-actions">
                    <button type="button" class="secondary" onclick="closeDeleteExpenseModal()">Cancel</button>
                    <button type="button" class="danger" id="confirm-delete-expense-btn" onclick="confirmDeleteExpense()">Delete</button>
                </div>
            </div>
        `;
        document.body.appendChild(modalOverlay);
        
        // Close modal when clicking outside
        modalOverlay.addEventListener('click', function(event) {
            if (event.target === modalOverlay) {
                closeDeleteExpenseModal();
            }
        });
    }

    // Update expense description in modal
    const descriptionEl = document.getElementById('delete-expense-description');
    if (descriptionEl) {
        descriptionEl.textContent = expense.description || '';
    }

    // Store expense ID and group ID for deletion
    modalOverlay.dataset.expenseId = expense.id;
    modalOverlay.dataset.groupId = expense.groupId;

    modalOverlay.classList.add('active');
}

function closeDeleteExpenseModal() {
    const modalOverlay = document.getElementById('delete-expense-modal');
    if (modalOverlay) {
        modalOverlay.classList.remove('active');
    }
}

function confirmDeleteExpense() {
    const modalOverlay = document.getElementById('delete-expense-modal');
    if (!modalOverlay) {
        return;
    }

    const expenseId = modalOverlay.dataset.expenseId;
    const groupId = modalOverlay.dataset.groupId;

    if (!expenseId || !groupId) {
        showError('Expense information not available');
        return;
    }

    if (!currentToken) {
        showError('You must be logged in to delete an expense');
        closeDeleteExpenseModal();
        return;
    }

    // Disable delete button during submission
    const deleteButton = document.getElementById('confirm-delete-expense-btn');
    const originalText = deleteButton.textContent;
    deleteButton.disabled = true;
    deleteButton.textContent = 'Deleting...';

    fetch(`${API_BASE}/groups/${groupId}/expenses/${expenseId}`, {
        method: 'DELETE',
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
                    throw new Error('You do not have permission to delete this expense');
                }
                if (response.status === 404) {
                    throw new Error('Expense not found');
                }
                return response.json().then(data => {
                    throw new Error(data.message || 'Failed to delete expense');
                });
            }
            // DELETE returns 204 No Content, so no JSON to parse
            return null;
        })
        .then(() => {
            closeDeleteExpenseModal();
            // Reload expenses data
            fetchGroupExpenses(groupId);
        })
        .catch(error => {
            console.error('Error:', error);
            showError(error.message || 'Failed to delete expense');
        })
        .finally(() => {
            deleteButton.disabled = false;
            deleteButton.textContent = originalText;
        });
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

