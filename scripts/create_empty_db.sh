#!/bin/bash
# Script to create an empty database with just the schema loaded.
#
# This creates database/costsharing.db with the schema but no data.

DB_PATH="database/costsharing.db"
SCHEMA_FILE="src/cost_sharing/sql/schema-sqlite.sql"

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

# Create database with schema
echo "Creating database with schema..."
sqlite3 "$DB_PATH" < "$SCHEMA_FILE"

if [ $? -eq 0 ]; then
    echo "Successfully created empty database at $DB_PATH"
else
    echo "Error: Failed to create database"
    exit 1
fi

