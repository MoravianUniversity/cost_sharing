
## Overview

The Cost Sharing application helps groups of people (roommates, friends, project teams, etc.) track shared expenses and determine how much each person owes. When someone pays for a shared expense, the system splits the cost among specified participants and maintains running balances for the group.


## Example: Roommates Sharing Expenses

The example is taken from the [Sample Dataset](docs/sample-dataset.md).

### The Group: "Roommates Spring 2025"

**Members:**
- Charlie (group creator)
- Alice
- David

### The Expenses

1. **Grocery shopping** (Jan 10, 2025)
   - Paid by: Charlie
   - Split between: Charlie & Alice
   - Amount: $86.40
   - Per person: $43.20

2. **Utilities bill** (Jan 15, 2025)
   - Paid by: Alice
   - Split between: Charlie & Alice
   - Amount: $120.00
   - Per person: $60.00

3. **Restaurant dinner** (Jan 20, 2025)
   - Paid by: David
   - Split between: Alice & David
   - Amount: $67.89
   - Per person: $33.95

4. **Internet bill** (Jan 25, 2025)
   - Paid by: Alice
   - Split between: Charlie, Alice & David (all three roommates)
   - Amount: $100.00
   - Per person: $33.33

### The Balances

After all expenses are recorded, the system calculates:

**Charlie:**
- Total paid: $86.40
- Total owed: $136.53 (his share of expenses #1, #2, and #4)
- **Net balance: -$50.13** (Charlie owes $50.13)

**Alice:**
- Total paid: $220.00 (expenses #2 and #4)
- Total owed: $170.48 (her share of all four expenses)
- **Net balance: +$49.52** (Alice is owed $49.52)

**David:**
- Total paid: $67.89
- Total owed: $67.28 (his share of expenses #3 and #4)
- **Net balance: +$0.61** (David is owed $0.61)


**Note on Rounding**: Notice that the Internet bill ($100.00 split 3 ways) results in $33.33 per person, which sums to $99.99 (not $100.00). This $0.01 rounding discrepancy is handled automatically - Alice paid the full $100.00, but only $99.99 is owed by participants, so the system accounts for this correctly in the final balances.


## Important System Features

### Core Functionality
- **Group Management**: Users can create groups and invite members (even if they haven't signed up yet)
- **Expense Tracking**: Users record expenses with description, amount, date, and who the expense is split between
- **Automatic Balance Calculation**: The system calculates who owes whom based on all expenses
- **Payer Ownership**: Only the person who paid for an expense can modify or delete it

### User Management
- **Google OAuth Authentication**: Users log in with their Google account
- **Flexible User Creation**: Users can be added to groups before they log in - accounts are created as needed
- **Multi-Group Membership**: Users can belong to multiple groups simultaneously

### Expense Splitting
- **Equal Splitting**: Expenses are split equally among specified participants
- **Flexible Participation**: Not all group members need to be included in every expense
- **Rounding Handling**: System handles currency rounding (rounds to 2 decimal places, with small discrepancies possible)

### Security & Permissions
- **Group-Based Access**: Only group members can view details of the group or add expenses to a group
- **Payer-Only Modification**: Only the person who paid can edit or delete their expenses
- **Member Protection**: A member can remove themselves from a group, and a creator can remove other members - but no member can be removed if they are involved in expenses.  Also, group creators cannot be removed.


## System Architecture

The system is organized as a three-tier architecture:

- **Database Layer**:  
  Uses an SQLite database for persistent storage. All group data, users, expenses, and transactions are saved in SQLite tables. The schema is designed to enforce data integrity via constraints, foreign keys, and validation rules.

- **Backend/API Layer**:  
  Uses Flask to provide a RESTful API that handles authentication (Google OAuth), authorization (permissions, group membership), business logic (expense splitting, rounding, balance calculations), and data validation.

- **Frontend Layer**:  
  Uses HTML, CSS, and JavaScript to provide a user interface.  The frontend allows users to log in, view and manage groups, add/edit expenses, and review balances in real time, with dynamic updates and validations handled in the browser.  It communicates with the Flask API via AJAX/fetch requests.


## Documentation

* [docs/usecases.md](docs/usecases.md) contains detailed use cases of the business logic for the system
* [docs/dev.md](docs/dev.md) contains directions to set up dev/prod environments.
* [docs/sample-dataset.md](docs/sample-dataset.md) contains data and discussion for some sample groups
* [src/cost_sharing/sql/schema-sqlite.sql](src/cost_sharing/sql/schema-sqlite.sql) contains schema for all database tables
* [src/cost_sharing/sql/sample-data.sql](src/cost_sharing/sql/sample-data.sql) contains the sample dataset in SQL format
* [docs/api.yaml](docs/api.yaml) contains an OpenAPI specification of all API endpoints.
* [docs/ui/README.md](docs/ui/README.md) contains HTML and CSS mockups web pages
