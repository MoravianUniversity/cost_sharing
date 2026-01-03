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
(6, 'frank@school.edu', 'Frank');

-- ============================================================================
-- GROUPS
-- ============================================================================

INSERT INTO groups (id, name, description, created_by_user_id) VALUES
(1, 'Weekend Trip Planning', 'Planning expenses for upcoming weekend getaway', 1),
(2, 'Roommates Spring 2025', 'Shared expenses for apartment 4B', 3),
(3, 'Project Team Expenses', 'Team project collaboration costs', 5);

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

