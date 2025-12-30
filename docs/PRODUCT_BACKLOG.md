# Product Backlog

This document contains all product backlog items (cards) for the Cost Sharing application. Cards are organized by category and can be tagged in your project management tool (e.g., Trello) by feature area or "infrastructure".

## Card Format

Each card will have:
- **Title**: Brief, actionable description
- **Description**: What needs to be done and why
- **Estimated Time**: 10-15 minutes
- **Dependencies**: Other cards that must be completed first
- **Guidance Level**: Description only, code provided, or step-by-step guide

## Project Standards

Before starting development, teams should establish:

- **Testing**: 90% code coverage for Flask backend (pytest + pytest-cov)
- **Code Review**: PRs must be reviewed and merged by someone other than the author
- **Linting**: All code must pass linting checks (linting rules file will be provided)
- **CI/CD**: Automated tests and deployment on PR merge

---

## Infrastructure & Foundation Cards

### INF-001: Set Up Flask Project Structure
**Description**: Create the basic Flask application structure with proper folder organization (app/, tests/, requirements.txt, etc.). Set up a minimal Flask app that can run locally.

**Guidance**: Description with folder structure template

**Dependencies**: None

---

### INF-002: Initialize Database with Schema
**Description**: Set up SQLite database using the provided schema file. Create database initialization script that can be run to set up the database structure.

**Guidance**: Schema SQL file provided, description of how to initialize

**Dependencies**: INF-001

---

### INF-003: Load Sample Data into Database
**Description**: Create script or command to load the provided sample data SQL file into the database for development and testing.

**Guidance**: Sample data SQL file provided

**Dependencies**: INF-002

---

### INF-004: Set Up Testing Framework
**Description**: Configure pytest and pytest-cov for the project. Set up test directory structure and create a basic test to verify the testing setup works.

**Guidance**: Description with example test

**Dependencies**: INF-001

---

### INF-005: Configure Linting Rules
**Description**: Set up linting tool (e.g., flake8, pylint) with provided configuration file. Ensure linting can be run locally and in CI.

**Guidance**: Linting config file provided

**Dependencies**: INF-001

---

### INF-006: Set Up Basic Frontend Structure
**Description**: Create basic HTML/CSS/JavaScript file structure for the frontend. Set up a simple page that can make API calls to verify the frontend-backend connection works.

**Guidance**: Description with basic structure template

**Dependencies**: INF-001

---

### INF-007: Set Up GitHub Repository and Branch Workflow
**Description**: Initialize Git repository, set up main/master branch, and establish branch naming conventions. Create initial commit with project structure.

**Guidance**: Description of Git workflow

**Dependencies**: INF-001

---

### INF-008: Configure GitHub Actions for Testing
**Description**: Set up GitHub Actions workflow that runs tests and linting on pull requests. Ensure tests must pass before PR can be merged.

**Guidance**: Step-by-step guide with example workflow file

**Dependencies**: INF-004, INF-005, INF-007

---

### INF-009: Set Up EC2 Instance
**Description**: Provision and configure EC2 instance for production deployment. Set up basic security groups and access.

**Guidance**: Step-by-step guide

**Dependencies**: None (can be done in parallel)

---

### INF-010: Configure Domain and SSL
**Description**: Configure provided subdomain (teamname.moraviancs.click) to point to EC2 instance. Set up SSL certificate (Let's Encrypt or similar).

**Guidance**: Step-by-step guide

**Dependencies**: INF-009

---

### INF-011: Set Up CI/CD Deployment Pipeline
**Description**: Configure GitHub Actions to automatically deploy to EC2 instance when PR is merged to main branch. Include steps for running tests, building, and deploying.

**Guidance**: Step-by-step guide with example workflow

**Dependencies**: INF-008, INF-009, INF-010

---

### INF-012: Document Development Environment Setup
**Description**: Create documentation (README or SETUP.md) explaining how to set up the development environment locally, including installing dependencies, setting up database, and running the application.

**Guidance**: Description of what should be included

**Dependencies**: INF-001, INF-002, INF-003

---

### INF-013: Document CI/CD Process
**Description**: Create documentation explaining the CI/CD pipeline, how deployments work, and how to troubleshoot common issues.

**Guidance**: Description of what should be included

**Dependencies**: INF-011

---

## Authentication Feature Cards

### AUTH-001: Implement Google OAuth Authentication
**Description**: Set up Google OAuth integration for user authentication. Implement OAuth callback endpoint that creates user accounts on first login.

**Sub-cards**:
- AUTH-001a: Configure Google OAuth credentials
- AUTH-001b: Implement GET /auth/callback endpoint
- AUTH-001c: Implement GET /auth/me endpoint
- AUTH-001d: Create frontend login page
- AUTH-001e: Implement token storage and API request authentication

**Guidance**: Strong scaffolding - step-by-step guide or pre-configured setup

**Dependencies**: INF-001, INF-002

---

## Group Management Feature Cards

### GRP-001: Implement Group Listing
**Description**: Allow authenticated users to see all groups they belong to.

**Sub-cards**:
- GRP-001a: Implement GET /groups endpoint (backend)
- GRP-001b: Write tests for GET /groups endpoint
- GRP-001c: Create frontend page to display user's groups

**Guidance**: Description with API spec reference

**Dependencies**: INF-001, INF-002, INF-004, INF-006

---

### GRP-002: Implement Group Creation
**Description**: Allow authenticated users to create new groups.

**Sub-cards**:
- GRP-002a: Implement POST /groups endpoint (backend)
- GRP-002b: Write tests for POST /groups endpoint
- GRP-002c: Create frontend form to create new groups

**Guidance**: Description with API spec reference

**Dependencies**: INF-001, INF-002, INF-004, INF-006

---

### GRP-003: Implement Group Details View
**Description**: Allow group members to view detailed information about a group, including all members.

**Sub-cards**:
- GRP-003a: Implement GET /groups/{groupId} endpoint (backend)
- GRP-003b: Write tests for GET /groups/{groupId} endpoint
- GRP-003c: Create frontend page to display group details

**Guidance**: Description with API spec reference

**Dependencies**: INF-001, INF-002, INF-004, INF-006

---

### GRP-004: Implement Group Deletion
**Description**: Allow group members to delete groups (only if no expenses exist).

**Sub-cards**:
- GRP-004a: Implement DELETE /groups/{groupId} endpoint (backend)
- GRP-004b: Write tests for DELETE /groups/{groupId} endpoint (including error cases)
- GRP-004c: Add delete functionality to frontend group details page

**Guidance**: Description with API spec reference

**Dependencies**: INF-001, INF-002, INF-004, INF-006, GRP-003

---

### GRP-005: Implement Add Member to Group
**Description**: Allow group members to add other users to a group by email. Creates placeholder accounts if user doesn't exist.

**Sub-cards**:
- GRP-005a: Implement POST /groups/{groupId}/members endpoint (backend)
- GRP-005b: Write tests for POST /groups/{groupId}/members endpoint (including placeholder creation)
- GRP-005c: Create frontend form to add members to group

**Guidance**: Description with API spec reference

**Dependencies**: INF-001, INF-002, INF-004, INF-006, GRP-003

---

### GRP-006: Implement Remove Member from Group
**Description**: Allow group members to remove other members (with appropriate restrictions).

**Sub-cards**:
- GRP-006a: Implement DELETE /groups/{groupId}/members/{userId} endpoint (backend)
- GRP-006b: Write tests for DELETE /groups/{groupId}/members/{userId} endpoint (including error cases)
- GRP-006c: Add remove member functionality to frontend group details page

**Guidance**: Description with API spec reference

**Dependencies**: INF-001, INF-002, INF-004, INF-006, GRP-003

---

## Expense Management Feature Cards

### EXP-001: Implement Create Expense
**Description**: Allow group members to create expenses. The authenticated user is automatically set as the payer.

**Sub-cards**:
- EXP-001a: Implement POST /groups/{groupId}/expenses endpoint (backend)
- EXP-001b: Write tests for POST /groups/{groupId}/expenses endpoint (including validation)
- EXP-001c: Create frontend form to create new expenses

**Guidance**: Description with API spec reference

**Dependencies**: INF-001, INF-002, INF-004, INF-006, GRP-001

---

### EXP-002: Implement List Group Expenses
**Description**: Allow group members to see all expenses for a group.

**Sub-cards**:
- EXP-002a: Implement GET /groups/{groupId}/expenses endpoint (backend)
- EXP-002b: Write tests for GET /groups/{groupId}/expenses endpoint
- EXP-002c: Create frontend page to display group expenses

**Guidance**: Description with API spec reference

**Dependencies**: INF-001, INF-002, INF-004, INF-006, GRP-001

---

### EXP-003: Implement View Expense Details
**Description**: Allow group members to view detailed information about a specific expense.

**Sub-cards**:
- EXP-003a: Implement GET /groups/{groupId}/expenses/{expenseId} endpoint (backend)
- EXP-003b: Write tests for GET /groups/{groupId}/expenses/{expenseId} endpoint
- EXP-003c: Create frontend page to display expense details

**Guidance**: Description with API spec reference

**Dependencies**: INF-001, INF-002, INF-004, INF-006, EXP-002

---

### EXP-004: Implement Update Expense
**Description**: Allow expense payers to update their expenses (only the payer can modify).

**Sub-cards**:
- EXP-004a: Implement PUT /groups/{groupId}/expenses/{expenseId} endpoint (backend)
- EXP-004b: Write tests for PUT /groups/{groupId}/expenses/{expenseId} endpoint (including authorization)
- EXP-004c: Create frontend form to update expenses

**Guidance**: Description with API spec reference

**Dependencies**: INF-001, INF-002, INF-004, INF-006, EXP-003

---

### EXP-005: Implement Delete Expense
**Description**: Allow expense payers to delete their expenses (only the payer can delete).

**Sub-cards**:
- EXP-005a: Implement DELETE /groups/{groupId}/expenses/{expenseId} endpoint (backend)
- EXP-005b: Write tests for DELETE /groups/{groupId}/expenses/{expenseId} endpoint (including authorization)
- EXP-005c: Add delete functionality to frontend expense details page

**Guidance**: Description with API spec reference

**Dependencies**: INF-001, INF-002, INF-004, INF-006, EXP-003

---

## Balance & Reconciliation Feature Cards

### BAL-001: Implement Group Balances Calculation
**Description**: Calculate and display current balances showing who owes whom in a group.

**Sub-cards**:
- BAL-001a: Implement GET /groups/{groupId}/balances endpoint (backend)
- BAL-001b: Write tests for GET /groups/{groupId}/balances endpoint (including rounding scenarios)
- BAL-001c: Create frontend page to display group balances

**Guidance**: Description with API spec reference and balance calculation algorithm

**Dependencies**: INF-001, INF-002, INF-004, INF-006, EXP-002

---

### BAL-002: Implement Optimized Settlement Plan (Stretch Goal)
**Description**: Calculate the minimum number of transactions needed to settle all debts.

**Sub-cards**:
- BAL-002a: Implement GET /groups/{groupId}/settlements endpoint (backend)
- BAL-002b: Write tests for GET /groups/{groupId}/settlements endpoint
- BAL-002c: Create frontend display for settlement plan

**Guidance**: Description with algorithm guidance

**Dependencies**: INF-001, INF-002, INF-004, INF-006, BAL-001

---

## Card Organization Notes

- **Infrastructure cards (INF-001 through INF-013)**: Should generally be completed early, especially INF-001 through INF-007
- **Feature cards**: Can be selected based on team priorities, but should ensure end-to-end functionality (frontend → API → database)
- **Sub-cards**: Break down feature work into smaller, manageable pieces
- **Testing**: All backend feature cards include testing sub-cards - tests should be written as part of feature implementation
- **Dependencies**: Pay attention to card dependencies when planning sprints

## Sprint Planning Guidance

For Sprint 1, teams should aim to:
1. Complete foundational infrastructure (INF-001 through INF-007 at minimum)
2. Implement at least one complete feature end-to-end (e.g., Group Management with frontend)
3. Have CI/CD pipeline in place (INF-008, INF-011)
4. Demonstrate that the "plumbing" works: frontend can call API, API can interact with database

Teams can choose which features to implement, but should ensure they have a demo-able system showing the full stack working together.

