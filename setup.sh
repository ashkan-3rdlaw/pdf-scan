#!/bin/bash

# setup.sh - Setup script for pdf-scan project on macOS
# This script installs required dependencies using Homebrew and sets up the project

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
print_info() {
    echo -e "${BLUE}ℹ ${NC}$1"
}

print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_header() {
    echo ""
    echo -e "${BLUE}=====================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}=====================================${NC}"
    echo ""
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS only."
    exit 1
fi

print_header "PDF Scan Project Setup for macOS"

# Check if Homebrew is installed
print_info "Checking for Homebrew..."
if ! command -v brew &> /dev/null; then
    print_error "Homebrew is not installed. Please install it first from https://brew.sh"
    exit 1
fi
print_success "Homebrew is already installed"
print_info "Updating Homebrew..."
brew update

# Install uv
print_header "Installing uv"
if command -v uv &> /dev/null; then
    print_success "uv is already installed (version: $(uv --version))"
    # Check if uv was installed via brew
    if brew list uv &> /dev/null; then
        print_info "Upgrading uv to latest version..."
        brew upgrade uv 2>&1 | grep -q "already installed" && print_info "uv is already up to date" || print_success "uv upgraded successfully"
    else
        print_info "uv was installed outside of Homebrew, skipping upgrade"
    fi
else
    print_info "Installing uv..."
    brew install uv
    print_success "uv installed successfully (version: $(uv --version))"
fi

# Install jq
print_header "Installing jq"
if command -v jq &> /dev/null; then
    print_success "jq is already installed (version: $(jq --version))"
else
    print_info "Installing jq..."
    brew install jq
    print_success "jq installed successfully (version: $(jq --version))"
fi

# Install Docker
print_header "Installing Docker"
if command -v docker &> /dev/null; then
    print_success "Docker is already installed (version: $(docker --version))"
else
    print_info "Installing Docker..."
    brew install --cask docker
    print_success "Docker installed successfully"
    print_warning "You may need to start Docker Desktop manually from Applications"
    print_warning "Please start Docker Desktop and then re-run this script"
    exit 0
fi

# Check if Docker is running
print_info "Checking if Docker is running..."
if ! docker info &> /dev/null; then
    print_error "Docker is installed but not running."
    print_warning "Please start Docker Desktop and then re-run this script"
    exit 1
else
    print_success "Docker is running"
fi

# Install docker-compose (if not already included with Docker Desktop)
if ! command -v docker-compose &> /dev/null; then
    print_info "Installing docker-compose..."
    brew install docker-compose
    print_success "docker-compose installed successfully"
else
    print_success "docker-compose is available (version: $(docker-compose --version))"
fi

# Python version check (optional but informative)
print_header "Python Environment"
if command -v python3 &> /dev/null; then
    print_success "Python3 is installed (version: $(python3 --version))"
else
    print_warning "Python3 is not installed. Installing via Homebrew..."
    brew install python@3.13
fi

# Run uv sync to set up project dependencies
print_header "Setting up Project Dependencies"
print_info "Running uv sync..."

if [ -f "pyproject.toml" ]; then
    uv sync
    print_success "Project dependencies synchronized successfully"
else
    print_error "pyproject.toml not found. Are you in the project root directory?"
    exit 1
fi

# Summary
print_header "Setup Complete!"
print_success "All dependencies have been installed:"
echo "  • Homebrew: $(brew --version | head -n1)"
echo "  • uv: $(uv --version)"
echo "  • jq: $(jq --version)"
echo "  • Docker: $(docker --version)"
echo "  • docker-compose: $(docker-compose --version)"
echo ""
print_info "Next steps:"
echo "  1. Start the services: docker-compose up -d"
echo "  2. Run the application: uv run python -m pdf_scan.main"
echo "  3. Run tests: ./scripts/run_all_tests.sh"
echo ""
print_success "Happy coding! 🚀"

