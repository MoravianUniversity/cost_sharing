-- Sample Data for Cost Sharing API
-- This script inserts sample data into the database.
-- Assumes the schema has already been created via schema-sqlite.sql
--
-- Enable foreign key constraints (required for SQLite)
PRAGMA foreign_keys = ON;

-- ============================================================================
-- USERS
-- ============================================================================

INSERT INTO users (id, email, name) VALUES
(1, 'alice@school.edu', 'Alice'),
(2, 'bob@school.edu', 'Bob'),
(3, 'charlie@school.edu', 'Charlie'),
(4, 'david@school.edu', 'David'),
(5, 'eve@school.edu', 'Eve'),
(6, 'frank@school.edu', 'Frank'),
(7, 'george@school.edu', 'George'),
(8, 'helen@school.edu', 'Helen'),
(9, 'iris@school.edu', 'Iris'),
(10, 'jack@school.edu', 'Jack'),
(11, 'kate@school.edu', 'Kate');

-- ============================================================================
-- GROUPS
-- ============================================================================

INSERT INTO groups (id, name, description, created_by_user_id) VALUES
(1, 'Weekend Trip Planning', 'Planning expenses for upcoming weekend getaway', 1),
(2, 'Roommates Spring 2025', 'Shared expenses for apartment 4B', 3),
(3, 'Project Team Expenses', 'Team project collaboration costs', 5),
(4, 'Study Group Fall 2025', 'Shared costs for study materials and snacks for our weekly study sessions', 8),
(5, 'Quick Split', NULL, 9),
(6, 'This is a group name that is exactly one hundred characters long to test maximum length validation  ', 'This is a group description that is exactly five hundred characters long to test the maximum length validation rule for group descriptions. It contains multiple sentences and demonstrates how the system handles descriptions at the upper limit of the allowed length. The description field can store up to 500 characters, and this example uses every single one of those characters to ensure proper validation and display handling. This is useful for testing edge cases in the user interface and API val', 10);

-- ============================================================================
-- GROUP MEMBERS
-- ============================================================================

-- Group 1: Alice (creator), Bob
INSERT INTO group_members (group_id, user_id) VALUES
(1, 1),
(1, 2);

-- Group 2: Charlie (creator), Alice, David
INSERT INTO group_members (group_id, user_id) VALUES
(2, 3),
(2, 1),
(2, 4);

-- Group 3: Eve (creator), Frank
INSERT INTO group_members (group_id, user_id) VALUES
(3, 5),
(3, 6);

-- Group 4: Helen (creator), Iris, Jack, Kate, Bob (large group with 5 members)
INSERT INTO group_members (group_id, user_id) VALUES
(4, 8),
(4, 9),
(4, 10),
(4, 11),
(4, 2);

-- Group 5: Iris (creator), Helen (group with null description)
INSERT INTO group_members (group_id, user_id) VALUES
(5, 9),
(5, 8);

-- Group 6: Jack (creator), Kate (group with max length fields)
INSERT INTO group_members (group_id, user_id) VALUES
(6, 10),
(6, 11);

-- ============================================================================
-- EXPENSES
-- ============================================================================

-- Group 2 Expenses
INSERT INTO expenses (id, group_id, description, amount, expense_date, paid_by_user_id) VALUES
(1, 2, 'Grocery shopping', 86.40, '2025-01-10', 3),
(2, 2, 'Utilities bill', 120.00, '2025-01-15', 1),
(3, 2, 'Restaurant dinner', 67.89, '2025-01-20', 4),
(4, 2, 'Internet bill', 100.00, '2025-01-25', 1);

-- Group 3 Expenses
INSERT INTO expenses (id, group_id, description, amount, expense_date, paid_by_user_id) VALUES
(5, 3, 'Team lunch', 45.67, '2025-02-01', 5);

-- Group 4 Expenses (large group with various split patterns)
INSERT INTO expenses (id, group_id, description, amount, expense_date, paid_by_user_id) VALUES
(6, 4, 'Textbooks', 250.00, '2025-02-05', 8),
(7, 4, 'Coffee and snacks', 35.50, '2025-02-10', 9),
(8, 4, 'Printing costs', 12.75, '2025-02-12', 10),
(9, 4, 'Group dinner', 125.33, '2025-02-15', 11);

-- Group 5 Expenses (group with null description)
INSERT INTO expenses (id, group_id, description, amount, expense_date, paid_by_user_id) VALUES
(10, 5, 'Quick expense', 25.00, '2025-02-20', 9);

-- Group 6 Expenses (group with max length fields)
INSERT INTO expenses (id, group_id, description, amount, expense_date, paid_by_user_id) VALUES
(11, 6, 'This is an expense description that is exactly two hundred characters long to test the maximum length validation rule for expense descriptions in the system. It demonstrates proper handling of edge ca', 50.00, '2025-02-25', 10);

-- ============================================================================
-- EXPENSE PARTICIPANTS
-- ============================================================================

-- Expense 1: Grocery shopping (paid by Charlie, split between Charlie & Alice)
INSERT INTO expense_participants (expense_id, user_id) VALUES
(1, 3),
(1, 1);

-- Expense 2: Utilities bill (paid by Alice, split between Charlie & Alice)
INSERT INTO expense_participants (expense_id, user_id) VALUES
(2, 3),
(2, 1);

-- Expense 3: Restaurant dinner (paid by David, split between Alice & David)
INSERT INTO expense_participants (expense_id, user_id) VALUES
(3, 1),
(3, 4);

-- Expense 4: Internet bill (paid by Alice, split between Charlie, Alice & David)
INSERT INTO expense_participants (expense_id, user_id) VALUES
(4, 3),
(4, 1),
(4, 4);

-- Expense 5: Team lunch (paid by Eve, split between Eve & Frank)
INSERT INTO expense_participants (expense_id, user_id) VALUES
(5, 5),
(5, 6);

-- Expense 6: Textbooks (paid by Helen, split between all 5 members of Group 4)
INSERT INTO expense_participants (expense_id, user_id) VALUES
(6, 8),
(6, 9),
(6, 10),
(6, 11),
(6, 2);

-- Expense 7: Coffee and snacks (paid by Iris, split between Iris, Jack, and Kate - subset of group)
INSERT INTO expense_participants (expense_id, user_id) VALUES
(7, 9),
(7, 10),
(7, 11);

-- Expense 8: Printing costs (paid by Jack, split between Jack and Kate only)
INSERT INTO expense_participants (expense_id, user_id) VALUES
(8, 10),
(8, 11);

-- Expense 9: Group dinner (paid by Kate, split between all 5 members - demonstrates 5-way split with rounding)
INSERT INTO expense_participants (expense_id, user_id) VALUES
(9, 8),
(9, 9),
(9, 10),
(9, 11),
(9, 2);

-- Expense 10: Quick expense (paid by Iris, split between Iris and Helen)
INSERT INTO expense_participants (expense_id, user_id) VALUES
(10, 9),
(10, 8);

-- Expense 11: Max length description expense (paid by Jack, split between Jack and Kate)
INSERT INTO expense_participants (expense_id, user_id) VALUES
(11, 10),
(11, 11);

