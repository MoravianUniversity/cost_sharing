#!/bin/bash
# Script to create a database with schema, sample data, and update Alice for dev use.
#
# This creates database/costsharing.db with:
# - Schema loaded
# - Sample data loaded
# - Alice's record updated to your email/name so you can log in and see the sample data

DB_PATH="database/costsharing.db"
SCHEMA_FILE="src/cost_sharing/sql/schema-sqlite.sql"
SAMPLE_DATA_FILE="src/cost_sharing/sql/sample-data.sql"

# Check if database already exists
if [ -f "$DB_PATH" ]; then
    echo "Warning: Database file already exists at $DB_PATH"
    read -p "Do you want to overwrite it? (y/n): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        echo "Aborted. Database file was not modified."
        exit 0
    fi
    rm "$DB_PATH"
    echo "Removed existing database file."
fi

# Create database directory if it doesn't exist
mkdir -p database

# Check if schema file exists
if [ ! -f "$SCHEMA_FILE" ]; then
    echo "Error: Schema file not found at $SCHEMA_FILE"
    exit 1
fi

# Check if sample data file exists
if [ ! -f "$SAMPLE_DATA_FILE" ]; then
    echo "Error: Sample data file not found at $SAMPLE_DATA_FILE"
    exit 1
fi

# Create database with schema
echo "Creating database with schema..."
sqlite3 "$DB_PATH" < "$SCHEMA_FILE"

if [ $? -ne 0 ]; then
    echo "Error: Failed to create database with schema"
    exit 1
fi

# Load sample data
echo "Loading sample data..."
sqlite3 "$DB_PATH" < "$SAMPLE_DATA_FILE"

if [ $? -ne 0 ]; then
    echo "Error: Failed to load sample data"
    exit 1
fi

# Verify Alice exists
ALICE_CHECK=$(sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM users WHERE id = 1;")
if [ "$ALICE_CHECK" -eq 0 ]; then
    echo "Error: Alice (user ID 1) not found after loading sample data."
    exit 1
fi

# Get user information for Alice
echo ""
echo "Sample data loaded successfully."
echo ""
echo "To log in with your Google account and see Alice's groups and expenses,"
echo "we need to update Alice's record with your information."
echo ""
read -p "Email (from your Google account): " email
read -p "Name (your full name): " name

# Validate inputs
if [ -z "$email" ]; then
    echo "Error: Email cannot be empty"
    exit 1
fi

if [ -z "$name" ]; then
    echo "Error: Name cannot be empty"
    exit 1
fi

# Check if email already exists for another user
EMAIL_ESC=$(echo "$email" | sed "s/'/''/g")
EXISTING=$(sqlite3 "$DB_PATH" "SELECT id FROM users WHERE email = '$EMAIL_ESC' AND id != 1;")
if [ -n "$EXISTING" ]; then
    echo "Warning: Email '$email' is already used by user ID $EXISTING"
    echo "Continuing anyway to update Alice's record..."
fi

# Update Alice's record
NAME_ESC=$(echo "$name" | sed "s/'/''/g")
sqlite3 "$DB_PATH" "UPDATE users SET email = '$EMAIL_ESC', name = '$NAME_ESC' WHERE id = 1;"

if [ $? -eq 0 ]; then
    echo ""
    echo "Successfully created sample database at $DB_PATH"
    echo "Alice's record updated:"
    echo "  Email: $email"
    echo "  Name: $name"
    echo ""
    echo "You can now log in with your Google account and see Alice's groups and expenses."
else
    echo "Error: Failed to update Alice's record"
    exit 1
fi

