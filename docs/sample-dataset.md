# Sample Dataset Documentation

This document provides example data for a collection of users in three different groups.  Each group is designed to have expenses that demonstrate features of the Cost Sharing application.


## Users

Each user has a name, email address (which must be unique), and list of groups.

| Name | Email | Group Membership |
|------|-------|------------------|
| Alice | alice@school.edu | Group 1 (creator), Group 2 |
| Bob | bob@school.edu | Group 1 |
| Charlie | charlie@school.edu | Group 2 (creator) |
| David | david@school.edu | Group 2 |
| Eve | eve@school.edu | Group 3 (creator) |
| Frank | frank@school.edu | Group 3 |


---

## Group 1: Empty Group

This group is made up of two users. There are no expenses associated with the group.


- **Name**: "Weekend Trip Planning"
- **Description**: "Planning expenses for upcoming weekend getaway"
- **Creator**: Alice (User ID: 1)
- **Members**:
  - Alice (User ID: 1) - Group creator
  - Bob (User ID: 2)

### Expenses

- **None** - No expenses have been added yet.


### Balances

Since there are no expenses, both Alice and Bob have a zero balance.


---

## Group 2: Active Group with Multiple Expense Patterns

This group contains 3 users that have logged in at least once.  Each member has created at least one expense,
and these expenses demonstrate different subsets of group members as well as how costs are reported when the
shared cost produces fractional pennies.  Finally, this group demonstrates how fractional pennies
are combined when balances are computed.


### Group Details

- **Name**: "Roommates Spring 2025"
- **Description**: "Shared expenses for apartment 4B"
- **Creator**: Charlie (User ID: 3)
- **Members**:
  - Charlie (User ID: 3) - Group creator
  - Alice (User ID: 1) - Also a member of Group 1 (cross-group membership)
  - David (User ID: 4)

### Expenses

1. **Grocery shopping**
   - **Date**: 2025-01-10
   - **Paid by**: Charlie
   - **Split between**: Charlie, Alice
   - **Amount**: $86.40
   - **Per person**: $43.20

2. **Utilities bill**
   - **Date**: 2025-01-15
   - **Paid by**: Alice
   - **Split between**: Charlie, Alice
   - **Amount**: $120.00
   - **Per person**: $60.00

3. **Restaurant dinner**
   - **Date**: 2025-01-20
   - **Paid by**: David
   - **Split between**: Alice, David
   - **Amount**: $67.89
   - **Per person**: $33.95 (67.89 ÷ 2 = 33.945, rounds to 33.95)
   - **Note**: $33.95 × 2 = $67.90

4. **Internet bill**
   - **Date**: 2025-01-25
   - **Paid by**: Alice
   - **Split between**: Charlie, Alice, David
   - **Amount**: $100.00
   - **Per person**: $33.33 (100.00 ÷ 3 = 33.3333, rounds to $33.33)
   - **Note**: 3 × $33.33 = $99.99 (not $100.00)


### Balances

**Charlie:**
- **Total paid**: $86.40 (Expense #1)
- **Total owed**: $43.20 (Expense #1) + $60.00 (Expense #2) + $33.33 (Expense #4) = $136.53
- **Net balance**: $86.40 - $136.53 = **-$50.13** (owes $50.13)

**Alice:**
- **Total paid**: $120.00 (Expense #2) + $100.00 (Expense #4) = $220.00
- **Total owed**: $43.20 (Expense #1) + $60.00 (Expense #2) + $33.95 (Expense #3) + $33.33 (Expense #4) = $170.48
- **Net balance**: $220.00 - $170.48 = **+$49.52** (owed $49.52)

**David:**
- **Total paid**: $67.89 (Expense #3)
- **Total owed**: $33.95 (Expense #3) + $33.33 (Expense #4) = $67.28
- **Net balance**: $67.89 - $67.28 = **+$0.61** (owed $0.61)

*Note: The rounding in Expense #4 creates a small discrepancy. The expense amount is $100.00, but the per-person amounts sum to $99.99 (3 × $33.33), leaving $0.01 unallocated due to rounding. However, the net balances (-$50.13 + $49.52 + $0.61) correctly sum to $0.00, as Alice was paid $100.00 but only $99.99 is owed by participants.*



---

## Group 3: Group with Expense

This group has two members. The creator of the group has already added an expense.

### Group Details
- **Name**: "Project Team Expenses"
- **Description**: "Team project collaboration costs"
- **Creator**: Eve (User ID: 5)
- **Members**:
  - Eve (User ID: 5) - Group creator
  - Frank (User ID: 6)

### Expenses

1. **Team lunch**
   - **Date**: 2025-02-01
   - **Paid by**: Eve (creator)
   - **Split between**: Eve, Frank
   - **Amount**: $45.67
   - **Per person**: $22.84 (45.67 ÷ 2 = 22.835, rounds to 22.84)

### Balances

**Eve:**
- **Total paid**: $45.67 (Expense #1)
- **Total owed**: $22.84 (Expense #1)
- **Net balance**: $45.67 - $22.84 = **+$22.83** (owed $22.83)

**Frank:**
- **Total paid**: $0.00 (no expenses paid)
- **Total owed**: $22.84 (Expense #1)
- **Net balance**: $0.00 - $22.84 = **-$22.84** (owes $22.84)

