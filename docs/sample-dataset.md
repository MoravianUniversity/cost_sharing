# Sample Dataset Documentation

This document provides example data for a collection of users in six different groups.  Each group is designed to have expenses that demonstrate features of the Cost Sharing application, including edge cases and validation scenarios.

**This dataset is used in testing.** The sample data is defined in `src/cost_sharing/sql/sample-data.sql` and loaded into test databases via fixtures in `tests/conftest.py`. Test helper functions in `tests/helpers.py` reference this data for assertions. See the test files for examples of how this data is used.


## Users

Each user has a name, email address (which must be unique), and list of groups.

| Name | Email | Group Membership |
|------|-------|------------------|
| Alice | alice@school.edu | Group 1 (creator), Group 2 |
| Bob | bob@school.edu | Group 1, Group 4 |
| Charlie | charlie@school.edu | Group 2 (creator) |
| David | david@school.edu | Group 2 |
| Eve | eve@school.edu | Group 3 (creator) |
| Frank | frank@school.edu | Group 3 |
| George | george@school.edu | None |
| Helen | helen@school.edu | Group 4 (creator), Group 5 |
| Iris | iris@school.edu | Group 4, Group 5 (creator) |
| Jack | jack@school.edu | Group 4, Group 6 (creator) |
| Kate | kate@school.edu | Group 4, Group 6 |


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


---

## Group 4: Large Group with Various Split Patterns

This group contains 5 members and demonstrates various expense splitting patterns including full group splits, subset splits, and rounding scenarios with larger groups.

### Group Details

- **Name**: "Study Group Fall 2025"
- **Description**: "Shared costs for study materials and snacks for our weekly study sessions"
- **Creator**: Helen (User ID: 8)
- **Members**:
  - Helen (User ID: 8) - Group creator
  - Iris (User ID: 9)
  - Jack (User ID: 10)
  - Kate (User ID: 11)
  - Bob (User ID: 2) - Also a member of Group 1 (cross-group membership)

### Expenses

1. **Textbooks**
   - **Date**: 2025-02-05
   - **Paid by**: Helen
   - **Split between**: Helen, Iris, Jack, Kate, Bob (all 5 members)
   - **Amount**: $250.00
   - **Per person**: $50.00

2. **Coffee and snacks**
   - **Date**: 2025-02-10
   - **Paid by**: Iris
   - **Split between**: Iris, Jack, Kate (subset of 3 members)
   - **Amount**: $35.50
   - **Per person**: $11.83 (35.50 ÷ 3 = 11.8333, rounds to 11.83)
   - **Note**: $11.83 × 3 = $35.49 (not $35.50)

3. **Printing costs**
   - **Date**: 2025-02-12
   - **Paid by**: Jack
   - **Split between**: Jack, Kate (subset of 2 members)
   - **Amount**: $12.75
   - **Per person**: $6.38 (12.75 ÷ 2 = 6.375, rounds to 6.38)
   - **Note**: $6.38 × 2 = $12.76 (not $12.75)

4. **Group dinner**
   - **Date**: 2025-02-15
   - **Paid by**: Kate
   - **Split between**: Helen, Iris, Jack, Kate, Bob (all 5 members)
   - **Amount**: $125.33
   - **Per person**: $25.07 (125.33 ÷ 5 = 25.066, rounds to 25.07)
   - **Note**: 5 × $25.07 = $125.35 (not $125.33)

### Balances

**Helen:**
- **Total paid**: $250.00 (Expense #1)
- **Total owed**: $50.00 (Expense #1) + $25.07 (Expense #4) = $75.07
- **Net balance**: $250.00 - $75.07 = **+$174.93** (owed $174.93)

**Iris:**
- **Total paid**: $35.50 (Expense #2)
- **Total owed**: $50.00 (Expense #1) + $11.83 (Expense #2) + $25.07 (Expense #4) = $86.90
- **Net balance**: $35.50 - $86.90 = **-$51.40** (owes $51.40)

**Jack:**
- **Total paid**: $12.75 (Expense #3)
- **Total owed**: $50.00 (Expense #1) + $11.83 (Expense #2) + $6.38 (Expense #3) + $25.07 (Expense #4) = $93.28
- **Net balance**: $12.75 - $93.28 = **-$80.53** (owes $80.53)

**Kate:**
- **Total paid**: $125.33 (Expense #4)
- **Total owed**: $50.00 (Expense #1) + $11.83 (Expense #2) + $6.38 (Expense #3) + $25.07 (Expense #4) = $93.28
- **Net balance**: $125.33 - $93.28 = **+$32.05** (owed $32.05)

**Bob:**
- **Total paid**: $0.00 (no expenses paid)
- **Total owed**: $50.00 (Expense #1) + $25.07 (Expense #4) = $75.07
- **Net balance**: $0.00 - $75.07 = **-$75.07** (owes $75.07)

*Note: The rounding in various expenses creates small discrepancies, but the net balances correctly account for these differences.*


---

## Group 5: Group with Empty Description

This group demonstrates how the system handles groups with empty descriptions, which is an edge case for validation and display.

### Group Details

- **Name**: "Quick Split"
- **Description**: "" (empty string - no description provided)
- **Creator**: Iris (User ID: 9)
- **Members**:
  - Iris (User ID: 9) - Group creator
  - Helen (User ID: 8)

### Expenses

1. **Quick expense**
   - **Date**: 2025-02-20
   - **Paid by**: Iris
   - **Split between**: Iris, Helen
   - **Amount**: $25.00
   - **Per person**: $12.50

### Balances

**Iris:**
- **Total paid**: $25.00 (Expense #1)
- **Total owed**: $12.50 (Expense #1)
- **Net balance**: $25.00 - $12.50 = **+$12.50** (owed $12.50)

**Helen:**
- **Total paid**: $0.00 (no expenses paid)
- **Total owed**: $12.50 (Expense #1)
- **Net balance**: $0.00 - $12.50 = **-$12.50** (owes $12.50)


---

## Group 6: Group with Maximum Length Fields

This group demonstrates validation edge cases with maximum length fields for group names, descriptions, and expense descriptions.

### Group Details

- **Name**: "This is a group name that is exactly one hundred characters long to test maximum length validation  " (exactly 100 characters)
- **Description**: "This is a group description that is exactly five hundred characters long to test the maximum length validation rule for group descriptions. It contains multiple sentences and demonstrates how the system handles descriptions at the upper limit of the allowed length. The description field can store up to 500 characters, and this example uses every single one of those characters to ensure proper validation and display handling. This is useful for testing edge cases in the user interface and API val" (exactly 500 characters)
- **Creator**: Jack (User ID: 10)
- **Members**:
  - Jack (User ID: 10) - Group creator
  - Kate (User ID: 11)

### Expenses

1. **Max length description expense**
   - **Date**: 2025-02-25
   - **Paid by**: Jack
   - **Split between**: Jack, Kate
   - **Amount**: $50.00
   - **Per person**: $25.00
   - **Description**: "This is an expense description that is exactly two hundred characters long to test the maximum length validation rule for expense descriptions in the system. It demonstrates proper handling of edge ca" (exactly 200 characters)

### Balances

**Jack:**
- **Total paid**: $50.00 (Expense #1)
- **Total owed**: $25.00 (Expense #1)
- **Net balance**: $50.00 - $25.00 = **+$25.00** (owed $25.00)

**Kate:**
- **Total paid**: $0.00 (no expenses paid)
- **Total owed**: $25.00 (Expense #1)
- **Net balance**: $0.00 - $25.00 = **-$25.00** (owes $25.00)

