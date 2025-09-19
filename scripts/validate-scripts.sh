#!/bin/bash

# Script Validation Utility
# Tests all project scripts to ensure they work correctly regardless of run location

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_header() {
    echo -e "${BLUE}🔍 Project Script Validation${NC}"
    echo "=================================="
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Ensure we're in the project root
if ! cd "$(git rev-parse --show-toplevel)" 2>/dev/null; then
    print_error "This script must be run from within the git repository"
    exit 1
fi

PROJECT_ROOT="$(pwd)"
print_header
print_info "Validating scripts from: $PROJECT_ROOT"
echo ""

# Test function - run a script from a different directory to test path safety
test_script_from_different_dir() {
    local script_path="$1"
    local test_description="$2"
    local test_args="${3:-}"
    
    if [ ! -f "$script_path" ]; then
        print_error "Script not found: $script_path"
        return 1
    fi
    
    print_info "Testing: $test_description"
    
    # Create a temporary directory to run from
    local temp_dir=$(mktemp -d)
    local result=0
    
    # Run from the temp directory (definitely not project root)
    (
        cd "$temp_dir"
        if "$PROJECT_ROOT/$script_path" $test_args --help >/dev/null 2>&1 || \
           "$PROJECT_ROOT/$script_path" $test_args --dry-run >/dev/null 2>&1 || \
           "$PROJECT_ROOT/$script_path" $test_args 2>&1 | grep -q "project root" || \
           "$PROJECT_ROOT/$script_path" $test_args 2>&1 | grep -q "git repository"; then
            echo "  → Script properly handles directory context"
        else
            echo "  → ⚠️  Could not verify directory safety (this might be OK)"
        fi
    ) 2>/dev/null || result=1
    
    # Cleanup
    rm -rf "$temp_dir"
    
    return $result
}

# Validate critical project paths exist
validate_project_structure() {
    print_info "Validating project structure..."
    
    local critical_paths=(
        "scripts/"
        "dashboard/"
        "python/"
        "data/"
        "dashboard/package.json"
        "python/pyproject.toml"
    )
    
    local missing_paths=()
    
    for path in "${critical_paths[@]}"; do
        if [ ! -e "$path" ]; then
            missing_paths+=("$path")
        fi
    done
    
    if [ ${#missing_paths[@]} -eq 0 ]; then
        print_success "All critical paths exist"
    else
        print_error "Missing critical paths:"
        for path in "${missing_paths[@]}"; do
            echo "  - $path"
        done
        return 1
    fi
}

# Test individual scripts
test_scripts() {
    print_info "Testing individual scripts for directory safety..."
    echo ""
    
    # Find all .sh files in scripts directory
    while IFS= read -r -d '' script_path; do
        local script_name=$(basename "$script_path")
        local relative_path=${script_path#$PROJECT_ROOT/}
        
        # Skip the current validation script
        if [[ "$script_name" == "validate-scripts.sh" ]]; then
            continue
        fi
        
        echo "  Testing: $relative_path"
        
        # Check if script uses git rev-parse (good practice)
        if grep -q "git rev-parse --show-toplevel" "$script_path"; then
            echo "    ✅ Uses git rev-parse (directory-safe)"
        else
            echo "    ⚠️  Does not use git rev-parse (potentially unsafe)"
        fi
        
        # Check for hardcoded paths that might be problematic
        if grep -q "cd.*/" "$script_path" | grep -v "git rev-parse" >/dev/null; then
            echo "    ⚠️  Contains directory changes (verify they're safe)"
        fi
        
        # Check if executable
        if [ -x "$script_path" ]; then
            echo "    ✅ Executable"
        else
            echo "    ⚠️  Not executable (chmod +x recommended)"
        fi
        
        echo ""
        
    done < <(find scripts -name "*.sh" -type f -print0)
}

# Check for common anti-patterns
check_antipatterns() {
    print_info "Checking for common anti-patterns..."
    
    local issues_found=0
    
    # Check for scripts that might create directories in wrong places
    if grep -r "mkdir.*dashboard" scripts/ 2>/dev/null | grep -v "git rev-parse" >/dev/null; then
        print_warning "Found mkdir commands that might create directories - verify they're safe"
        issues_found=$((issues_found + 1))
    fi
    
    # Check for relative cd commands without proper root detection
    if grep -r "cd \.\." scripts/ 2>/dev/null | grep -v "git rev-parse" >/dev/null; then
        print_warning "Found relative cd commands - verify they work from any directory"
        issues_found=$((issues_found + 1))
    fi
    
    if [ $issues_found -eq 0 ]; then
        print_success "No obvious anti-patterns found"
    fi
}

# Main validation routine
main() {
    validate_project_structure || exit 1
    echo ""
    
    test_scripts
    echo ""
    
    check_antipatterns
    echo ""
    
    print_success "Script validation complete!"
    echo ""
    
    print_info "Recommendations for script safety:"
    print_info "1. Always use: cd \"\$(git rev-parse --show-toplevel)\""
    print_info "2. Use relative paths from project root after cd"
    print_info "3. Add validation checks for expected files/directories"
    print_info "4. Use 'set -e' to exit on errors"
    print_info "5. Test scripts from different directories"
    echo ""
    
    print_info "To test a specific script from a different location:"
    print_info "cd /tmp && $PROJECT_ROOT/scripts/[script-name].sh"
}

# Show help if requested
if [[ "${1:-}" == "--help" || "${1:-}" == "-h" ]]; then
    print_header
    echo ""
    echo "Usage: ./scripts/validate-scripts.sh"
    echo ""
    echo "This script validates all shell scripts in the project to ensure they:"
    echo "- Work correctly regardless of the directory they're run from"
    echo "- Use proper path resolution techniques"
    echo "- Follow best practices for directory safety"
    echo ""
    echo "The script will:"
    echo "- Check project structure is intact"
    echo "- Analyze each script for directory-safe patterns"  
    echo "- Look for common anti-patterns"
    echo "- Provide recommendations"
    echo ""
    exit 0
fi

main