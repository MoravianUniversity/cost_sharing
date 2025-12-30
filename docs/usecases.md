# Use Cases for Cost Sharing Application

This document outlines the complete list of use cases for the Cost Sharing application, organized by functional area and actor role.


## Authentication & User Management

### UC-AUTH-001: First-time User Login via Google OAuth
**Actor**: New User  
**Precondition**: User has not previously logged into the system  
**Main Flow**:
1. User initiates Google OAuth login
2. System redirects to Google OAuth
3. User authenticates with Google
4. System receives OAuth callback with authorization code
5. System exchanges code for user information
6. System creates new user account with email and name from OAuth
7. System generates and returns JWT token
8. User is logged in and can access the application

**Postcondition**: User account is created and active, user is authenticated

---

### UC-AUTH-002: Returning User Login via Google OAuth
**Actor**: Existing User  
**Precondition**: User has previously logged in and has an active account  
**Main Flow**:
1. User initiates Google OAuth login
2. System redirects to Google OAuth
3. User authenticates with Google
4. System receives OAuth callback with authorization code
5. System exchanges code for user information
6. System matches OAuth provider ID to existing user account
7. System generates and returns JWT token
8. User is logged in and can access the application

**Postcondition**: User is authenticated with valid token

---

### UC-AUTH-003: Placeholder User Activation
**Actor**: Placeholder User (invited but never logged in)  
**Precondition**: User was added to a group as a placeholder (email/name only, no OAuth)  
**Main Flow**:
1. Placeholder user initiates Google OAuth login
2. System receives OAuth callback with authorization code
3. System exchanges code for user information
4. System matches email from OAuth to existing placeholder account
5. System activates placeholder account by:
   - Setting `is_placeholder` to false
   - Setting `oauth_provider_id` from OAuth
   - Updating name if different from placeholder
6. System generates and returns JWT token
7. User is logged in and can access the application

**Postcondition**: Placeholder account is activated, user is authenticated

---

### UC-AUTH-004: Get Current User Information
**Actor**: Authenticated User  
**Precondition**: User has valid authentication token  
**Main Flow**:
1. User requests their own user information
2. System validates authentication token
3. System retrieves user account information
4. System returns user details (id, email, name)

**Postcondition**: User receives their account information

---

## Group Management

### UC-GROUP-001: Create a New Group
**Actor**: Authenticated User  
**Precondition**: User is logged in  
**Main Flow**:
1. User provides group name (required) and optional description
2. System validates name (1-100 characters) and description (max 500 characters)
3. System creates new group with authenticated user as creator
4. System automatically adds creator as a member of the group
5. System returns group details including ID

**Postcondition**: New group is created, creator is a member

---

### UC-GROUP-002: List User's Groups
**Actor**: Authenticated User  
**Precondition**: User is logged in  
**Main Flow**:
1. User requests list of their groups
2. System retrieves all groups where user is a member
3. System returns group summaries (id, name, description, memberCount)

**Postcondition**: User receives list of all groups they belong to

---

### UC-GROUP-003: View Group Details
**Actor**: Authenticated User (must be group member)  
**Precondition**: User is logged in and is a member of the group  
**Main Flow**:
1. User requests group details by group ID
2. System validates user is a member of the group
   - If user is not a member: System returns 403 Forbidden
3. System retrieves group information including:
   - Group details (id, name, description)
   - Creator information
   - List of all members
4. System returns complete group information

**Postcondition**: User views group details

---

### UC-GROUP-004: Delete a Group
**Actor**: Authenticated User (must be group member)  
**Precondition**: User is logged in and is a member of the group  
**Main Flow**:
1. User requests to delete a group by group ID
2. System validates user is a member of the group
   - If user is not a member: System returns 403 Forbidden
3. System checks if group has any expenses
   - If group has expenses: System returns 409 Conflict with error message, group is not deleted
4. If no expenses exist, system deletes the group (cascading to group_members)
5. System returns 204 No Content

**Postcondition**: Group is deleted

---

### UC-GROUP-005: Add Member to Group (Existing User)
**Actor**: Authenticated User (must be group member)  
**Precondition**: User is logged in, is a member of the group, and target user already has an account  
**Main Flow**:
1. User provides email and name of person to add
2. System validates email format
3. System checks if user with email already exists
4. System checks if user is already a member of the group
   - If user is already a member: System returns 409 Conflict with error message
5. If not already a member, system adds user to group
6. System returns member information and `isNewUser: false`

**Postcondition**: Existing user is added as group member

---

### UC-GROUP-006: Add Member to Group (New Placeholder User)
**Actor**: Authenticated User (must be group member)  
**Precondition**: User is logged in, is a member of the group, and target user does not have an account  
**Main Flow**:
1. User provides email and name of person to add
2. System validates email format
3. System checks if user with email exists
4. If user does not exist, system creates placeholder account:
   - Email and name from input
   - `is_placeholder` = true
   - `oauth_provider_id` = NULL
5. System adds placeholder user to group
6. System returns member information and `isNewUser: true`

**Postcondition**: Placeholder user account is created and added as group member

---

### UC-GROUP-007: Remove Member from Group (Self)
**Actor**: Authenticated User (removing themselves)  
**Precondition**: User is logged in, is a member of the group, is not the creator, and is not involved in any expenses  
**Main Flow**:
1. User requests to remove themselves from group
2. System validates user is a member
3. System checks if user is the group creator
   - If user is the group creator: System returns 409 Conflict: "Cannot remove group creator"
4. System checks if user is involved in any expenses (as paidBy or in splitBetween)
   - If user is involved in expenses: System returns 409 Conflict: "Cannot remove member who is involved in expenses"
5. If checks pass, system removes user from group
6. System returns 204 No Content

**Postcondition**: User is removed from group

---

### UC-GROUP-008: Remove Member from Group (Other Member)
**Actor**: Authenticated User (removing another member)  
**Precondition**: User is logged in, is a member of the group, target user is not the creator, and target user is not involved in any expenses  
**Main Flow**:
1. User requests to remove another member by user ID
2. System validates requesting user is a member
3. System validates target user exists and is a member
4. System checks if target user is the group creator
   - If target user is the group creator: System returns 409 Conflict: "Cannot remove group creator"
5. System checks if target user is involved in any expenses
   - If target user is involved in expenses: System returns 409 Conflict: "Cannot remove member who is involved in expenses"
6. If checks pass, system removes target user from group
7. System returns 204 No Content

**Postcondition**: Target user is removed from group

---

## Expense Management

### UC-EXP-001: Create New Expense
**Actor**: Authenticated User (must be group member)  
**Precondition**: User is logged in and is a member of the group  
**Main Flow**:
1. User provides expense details:
   - Description (required, 1-200 characters)
   - Amount (required, >= $0.01)
   - Date (required, ISO 8601 format YYYY-MM-DD)
   - splitBetween (required, array of user IDs, minimum 1)
2. System automatically sets paidBy to the authenticated user's ID (the caller is the payer)
3. System validates:
   - Authenticated user is included in splitBetween
   - All users in splitBetween are members of the group
   - Amount is valid (>= 0.01)
   - Description length is valid
   - If validation fails: System returns 400 Bad Request with specific validation error message
4. System creates expense record with paidBy set to authenticated user's ID
5. System creates expense_participant records for all users in splitBetween
6. System calculates perPersonAmount (amount / splitBetween.length, rounded to 2 decimals)
7. System returns expense details including calculated perPersonAmount

**Postcondition**: Expense is created and recorded with authenticated user as payer

---

### UC-EXP-002: List Group Expenses
**Actor**: Authenticated User (must be group member)  
**Precondition**: User is logged in and is a member of the group  
**Main Flow**:
1. User requests all expenses for a group
2. System validates user is a member of the group
   - If user is not a member: System returns 403 Forbidden
3. System retrieves all expenses for the group
4. For each expense, system includes:
   - Expense details (id, description, amount, date)
   - paidBy user information
   - splitBetween array with user information
   - Calculated perPersonAmount
5. System returns list of expenses

**Postcondition**: User views all group expenses

---

### UC-EXP-003: View Expense Details
**Actor**: Authenticated User (must be group member)  
**Precondition**: User is logged in and is a member of the group  
**Main Flow**:
1. User requests expense details by expense ID
2. System validates user is a member of the group
   - If user is not a member: System returns 403 Forbidden
3. System retrieves expense information
   - If expense does not exist: System returns 404 Not Found
4. System returns expense details including:
   - Expense details (id, description, amount, date)
   - paidBy user information
   - splitBetween array with user information
   - Calculated perPersonAmount

**Postcondition**: User views expense details

---

### UC-EXP-004: Update Expense
**Actor**: Authenticated User (must be group member and expense payer)  
**Precondition**: User is logged in, is a member of the group, expense exists, and user is the person who paid for the expense  
**Main Flow**:
1. User provides updated expense details:
   - Description (required, 1-200 characters)
   - Amount (required, >= $0.01)
   - Date (required, ISO 8601 format YYYY-MM-DD)
   - splitBetween (required, array of user IDs, minimum 1)
2. System validates user is a member of the group
   - If user is not a member: System returns 403 Forbidden
3. System validates expense exists
   - If expense does not exist: System returns 404 Not Found
4. System checks authorization: expense.paid_by_user_id must equal authenticated user's ID
   - If user is not the payer: System returns 403 Forbidden: "Only the person who paid for this expense can modify it"
5. System validates:
   - Authenticated user is included in splitBetween
   - All users in splitBetween are members of the group
   - Amount is valid (>= 0.01)
   - Description length is valid
   - If validation fails: System returns 400 Bad Request with validation error
6. System updates expense record (paidBy remains unchanged - cannot be modified)
7. System updates expense_participant records (delete old, create new)
8. System recalculates perPersonAmount
9. System returns updated expense details

**Postcondition**: Expense is updated (payer unchanged)

---

### UC-EXP-005: Delete Expense
**Actor**: Authenticated User (must be group member and expense payer)  
**Precondition**: User is logged in, is a member of the group, expense exists, and user is the person who paid for the expense  
**Main Flow**:
1. User requests to delete an expense by expense ID
2. System validates user is a member of the group
   - If user is not a member: System returns 403 Forbidden
3. System validates expense exists
   - If expense does not exist: System returns 404 Not Found
4. System checks authorization: expense.paid_by_user_id must equal authenticated user's ID
   - If user is not the payer: System returns 403 Forbidden: "Only the person who paid for this expense can delete it"
5. System deletes expense (cascading to expense_participants)
6. System returns 204 No Content

**Postcondition**: Expense is deleted

---

## Balance & Reconciliation

### UC-BAL-001: View Group Balances
**Actor**: Authenticated User (must be group member)  
**Precondition**: User is logged in and is a member of the group  
**Main Flow**:
1. User requests balances for a group
2. System validates user is a member of the group
   - If user is not a member: System returns 403 Forbidden
3. System retrieves all expenses for the group
4. System calculates balances:
   - For each expense, calculate perPersonAmount
   - Track total paid by each user
   - Track total owed by each user (sum of perPersonAmount for expenses they participated in)
   - Calculate net balance for each user (totalPaid - totalOwed)
   - Calculate pairwise debts (who owes whom)
5. System returns:
   - `balances`: Array of Balance objects showing pairwise debts (from, to, amount)
   - `summary`: Array of UserBalance objects showing per-user net balance, totalPaid, totalOwed

**Postcondition**: User views current group balances

**Notes**:
- Negative netBalance means user owes money
- Positive netBalance means user is owed money
- Rounding may cause small discrepancies (e.g., $100 split 3 ways = $33.33 × 3 = $99.99)

---

### UC-BAL-002: Get Optimized Settlement Plan (Stretch Goal)
**Actor**: Authenticated User (must be group member)  
**Precondition**: User is logged in and is a member of the group  
**Main Flow**:
1. User requests optimized settlement plan for a group
2. System validates user is a member of the group
   - If user is not a member: System returns 403 Forbidden
3. System calculates current balances (as in UC-BAL-001)
4. System calculates minimum number of transactions needed to settle all debts
5. System returns array of Settlement objects (from, to, amount)

**Postcondition**: User views optimized settlement plan

**Notes**:
- This is a stretch goal feature
- Algorithm should minimize number of transactions (e.g., if A owes B $10 and B owes C $10, result should be A pays C $10 directly)

---

## Error Handling & Edge Cases

### UC-ERR-001: Handle Invalid Authentication Token
**Actor**: Any User  
**Precondition**: User attempts to access protected endpoint  
**Main Flow**:
1. User makes request with invalid, expired, or missing token
2. System validates token
3. System returns 401 Unauthorized with generic error message
4. Error message does not reveal specific failure reason (token format, expiration, etc.)

**Postcondition**: User receives generic authentication error

---

### UC-ERR-002: Handle Access to Non-Member Group
**Actor**: Authenticated User  
**Precondition**: User is logged in but not a member of requested group  
**Main Flow**:
1. User attempts to access group resource (view, add expense, etc.)
2. System validates user is a member
3. System returns 403 Forbidden with generic error message
4. Error message does not reveal whether group exists or specific access reason

**Postcondition**: User receives generic authorization error

---

### UC-ERR-003: Handle Resource Not Found
**Actor**: Authenticated User  
**Precondition**: User requests non-existent resource  
**Main Flow**:
1. User requests resource by ID (group, expense, user)
2. System searches for resource
3. System cannot find resource
4. System returns 404 Not Found with specific error message

**Postcondition**: User receives not found error

---

### UC-ERR-004: Handle Rounding Discrepancies
**Actor**: System (automatic)  
**Precondition**: Expense amount does not divide evenly among participants  
**Main Flow**:
1. System calculates perPersonAmount = amount / splitBetween.length
2. System rounds perPersonAmount to 2 decimal places (round half up)
3. Sum of perPersonAmount × participants may differ from total amount by up to $0.01 per expense

**Postcondition**: Rounding handled consistently, small discrepancies may exist

**Example**: $100.00 split 3 ways = $33.33 each (total $99.99, not $100.00)

**Notes:** 
- System does NOT store perPersonAmount, it is computed when needed.


---

### UC-ERR-005: Handle Concurrent Expense Modifications
**Actor**: Multiple Users  
**Precondition**: Multiple users in same group  
**Note**: This use case identifies a potential ambiguity - the API does not specify how concurrent modifications are handled. This should be clarified in implementation.

**Potential Issues**:
- Two users update same expense simultaneously
- User deletes expense while another user is viewing/updating it
- User removes member while that member is creating an expense

**Recommendation**: Implement optimistic locking or transaction isolation
