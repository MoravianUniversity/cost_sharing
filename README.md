
## Overview

The Cost Sharing application helps groups of people (roommates, friends, project teams, etc.) track shared expenses and determine how much each person owes. When someone pays for a shared expense, the system splits the cost among specified participants and maintains running balances for the group.

**Key Concept**: Each expense is paid by one person but can be split among multiple group members. The system tracks both what each person has paid and what they owe.

## Important Features

### Core Functionality
- **Group Management**: Create groups and invite members (even if they haven't signed up yet)
- **Expense Tracking**: Record expenses with description, amount, date, and who the expense is split between
- **Automatic Balance Calculation**: System calculates who owes whom based on all expenses
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
- **Group-Based Access**: Only group members can view or add expenses to a group
- **Payer-Only Modification**: Only the person who paid can edit or delete their expenses
- **Creator Protection**: Group creators cannot be removed from groups

## Example: Roommates Sharing Expenses

Let's walk through a real example from the sample data - a group of three roommates sharing apartment expenses.

### The Group: "Roommates Spring 2025"

**Members:**
- Charlie (group creator)
- Alice
- David

### The Expenses

Over the course of January 2025, the roommates recorded several shared expenses:

1. **Grocery shopping** (Jan 10)
   - Paid by: Charlie
   - Split between: Charlie & Alice
   - Amount: $86.40
   - Per person: $43.20

2. **Utilities bill** (Jan 15)
   - Paid by: Alice
   - Split between: Charlie & Alice
   - Amount: $120.00
   - Per person: $60.00

3. **Restaurant dinner** (Jan 20)
   - Paid by: David
   - Split between: Alice & David
   - Amount: $67.89
   - Per person: $33.95

4. **Internet bill** (Jan 25)
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

### What This Means

The system shows that:
- Charlie should pay Alice $50.13
- David should pay Alice $0.61
- After these payments, all balances are settled

**Note on Rounding**: Notice that the Internet bill ($100.00 split 3 ways) results in $33.33 per person, which sums to $99.99 (not $100.00). This $0.01 rounding discrepancy is handled automatically - Alice paid the full $100.00, but only $99.99 is owed by participants, so the system accounts for this correctly in the final balances.

## Documentation Guide

This README provides a high-level overview. For implementation details, refer to these documents:

### Getting Started
1. **[API Specification](api.yaml)** - Complete OpenAPI 3.0 specification
   - All endpoints, request/response formats
   - Authentication requirements
   - Error codes and validation rules
   - **Start here** when implementing endpoints

2. **[Database Schema](schema-sqlite.sql)** - SQLite database structure
   - Table definitions and relationships
   - Foreign key constraints
   - Data types and validation rules
   - Implementation notes for Flask/SQLAlchemy

### Understanding the System
3. **[Use Cases](usecases.md)** - Complete list of use cases
   - Step-by-step flows for each feature
   - Error handling scenarios
   - Edge cases and validation rules
   - **Read this** to understand expected behavior

4. **[Sample Dataset](sample-dataset.md)** - Example data walkthrough
   - Three example groups with different scenarios
   - Balance calculations explained
   - Rounding examples
   - **Use this** to verify your implementation

### Testing & Development
5. **[Sample Data SQL](sample-data.sql)** - SQL script to populate database
   - Ready-to-use test data
   - Run this after creating your schema
   - Matches the sample dataset documentation

## Quick Start for Implementation

1. **Read the API spec** (`api.yaml`) to understand endpoints
2. **Review the schema** (`schema-sqlite.sql`) to design your database models
3. **Study the use cases** (`usecases.md`) to understand business logic
4. **Load sample data** (`sample-data.sql`) to test your implementation
5. **Verify with sample dataset** (`sample-dataset.md`) to check calculations

## Key Implementation Notes

- **Authentication**: Uses Google OAuth with JWT tokens (Bearer authentication)
- **Database**: SQLite for simplicity (suitable for class project scale)
- **Currency**: All amounts in dollars, stored as NUMERIC(10,2)
- **Rounding**: Per-person amounts rounded to 2 decimal places (round half up)
- **Validation**: Most validation rules enforced in application layer, not database
- **Permissions**: Group membership required for most operations; payer-only for expense modifications

## System Constraints

- Users can only create expenses they paid for (payer = creator)
- Group creators cannot be removed
- Members involved in expenses cannot be removed
- Groups with expenses cannot be deleted
- Expenses must include the payer in the split

