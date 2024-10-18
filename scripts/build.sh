#!/bin/bash

###
# [Legacy] This script builds a .zip packge of the lambda.
###

# Exit on any error
set -e

# Check if the script is being run from the project root
if [[ ! -d "./src" || ! -d "./scripts" ]]; then
    echo "Error: This script must be run from the project root directory."
    echo "Current directory: $(pwd)"
    echo "Usage: ./scripts/build_lambda_package.sh"
    exit 1
fi

# Define variables
PROJECT_ROOT="$(pwd)"
SRC_DIR="$PROJECT_ROOT/src"
BUILD_DIR="$PROJECT_ROOT/build"
PACKAGE_DIR="$BUILD_DIR/package"
ARTIFACT_NAME="lambda_function.zip"

# Check if pyproject.toml exists in the src directory
if [[ ! -f "$SRC_DIR/pyproject.toml" ]]; then
    echo "Error: pyproject.toml not found in $SRC_DIR"
    exit 1
fi

# Clean up any existing build artifacts
rm -rf "$BUILD_DIR"
mkdir -p "$PACKAGE_DIR"

# Copy project files
cp -R "$SRC_DIR/bucha" "$PACKAGE_DIR/"
cp "$SRC_DIR/main.py" "$PACKAGE_DIR/"

# Use Poetry to export dependencies
cd "$SRC_DIR"
poetry export -f requirements.txt --output "$BUILD_DIR/requirements.txt" --without-hashes
cd "$PROJECT_ROOT"

# Create a temporary virtual environment for installing dependencies
python -m venv "$BUILD_DIR/temp_venv"
source "$BUILD_DIR/temp_venv/bin/activate"

# Install dependencies into the package directory
pip install -r "$BUILD_DIR/requirements.txt" --target "$PACKAGE_DIR"

# Deactivate the temporary virtual environment
deactivate

# Remove the temporary virtual environment
rm -rf "$BUILD_DIR/temp_venv"

# Create deployment package
cd "$PACKAGE_DIR"
zip -r "$PROJECT_ROOT/$ARTIFACT_NAME" .

echo "Deployment package created: $PROJECT_ROOT/$ARTIFACT_NAME"