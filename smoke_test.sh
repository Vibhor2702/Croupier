#!/bin/bash

# Croupier Smoke Test Script
# This script performs end-to-end testing of all API endpoints

set -e  # Exit on any error

BASE_URL="http://localhost:8000"
ORG_NAME="smoke_test_org_$(date +%s)"
ADMIN_EMAIL="admin_$(date +%s)@smoketest.com"
ADMIN_PASSWORD="SmokeTest123"
NEW_ORG_NAME="smoke_test_renamed_$(date +%s)"
NEW_EMAIL="newemail_$(date +%s)@smoketest.com"

echo "=========================================="
echo "  Croupier Smoke Test - Full Workflow"
echo "=========================================="
echo ""
echo "[INFO] Testing against: $BASE_URL"
echo "[INFO] Organization: $ORG_NAME"
echo ""

# Color codes for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print test step
print_step() {
    echo ""
    echo "${YELLOW}[$1]${NC} $2"
    echo "----------------------------------------"
}

# Function to print success
print_success() {
    echo "${GREEN}✓ SUCCESS:${NC} $1"
}

# Function to print error and exit
print_error() {
    echo "${RED}✗ FAILED:${NC} $1"
    exit 1
}

# Step 1: Create Organization
print_step "STEP 1" "Creating new organization"
CREATE_RESPONSE=$(curl -s -X POST "$BASE_URL/org/create" \
    -H "Content-Type: application/json" \
    -d "{
        \"organization_name\": \"$ORG_NAME\",
        \"email\": \"$ADMIN_EMAIL\",
        \"password\": \"$ADMIN_PASSWORD\"
    }")

echo "$CREATE_RESPONSE" | jq '.' 2>/dev/null || echo "$CREATE_RESPONSE"

if echo "$CREATE_RESPONSE" | grep -q "\"organization_name\""; then
    print_success "Organization created successfully"
else
    print_error "Failed to create organization"
fi

# Step 2: Admin Login
print_step "STEP 2" "Logging in as admin"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/admin/login" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$ADMIN_EMAIL\",
        \"password\": \"$ADMIN_PASSWORD\"
    }")

echo "$LOGIN_RESPONSE" | jq '.' 2>/dev/null || echo "$LOGIN_RESPONSE"

# Extract JWT token
TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token' 2>/dev/null)

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    print_error "Failed to obtain JWT token"
fi

print_success "Login successful. Token obtained."
echo "[INFO] Token: ${TOKEN:0:50}..."

# Step 3: Get Organization
print_step "STEP 3" "Retrieving organization details"
GET_RESPONSE=$(curl -s -X GET "$BASE_URL/org/get?organization_name=$ORG_NAME")

echo "$GET_RESPONSE" | jq '.' 2>/dev/null || echo "$GET_RESPONSE"

if echo "$GET_RESPONSE" | grep -q "\"organization_name\""; then
    print_success "Organization retrieved successfully"
else
    print_error "Failed to retrieve organization"
fi

# Step 4: Update Organization
print_step "STEP 4" "Updating organization details"
UPDATE_RESPONSE=$(curl -s -X PUT "$BASE_URL/org/update" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{
        \"organization_name\": \"$NEW_ORG_NAME\",
        \"email\": \"$NEW_EMAIL\",
        \"password\": \"$ADMIN_PASSWORD\"
    }")

echo "$UPDATE_RESPONSE" | jq '.' 2>/dev/null || echo "$UPDATE_RESPONSE"

if echo "$UPDATE_RESPONSE" | grep -q "\"organization_name\""; then
    print_success "Organization updated successfully"
    # Update org name for delete step
    ORG_NAME="$NEW_ORG_NAME"
    ADMIN_EMAIL="$NEW_EMAIL"
else
    print_error "Failed to update organization"
fi

# Re-login with new credentials
print_step "STEP 4.1" "Re-logging in with updated credentials"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/admin/login" \
    -H "Content-Type: application/json" \
    -d "{
        \"email\": \"$ADMIN_EMAIL\",
        \"password\": \"$ADMIN_PASSWORD\"
    }")

TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token' 2>/dev/null)

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    print_error "Failed to re-login with updated credentials"
fi

print_success "Re-login successful"

# Step 5: Delete Organization
print_step "STEP 5" "Deleting organization"
DELETE_RESPONSE=$(curl -s -w "\n%{http_code}" -X DELETE "$BASE_URL/org/delete" \
    -H "Authorization: Bearer $TOKEN")

HTTP_CODE=$(echo "$DELETE_RESPONSE" | tail -n1)

if [ "$HTTP_CODE" == "204" ]; then
    print_success "Organization deleted successfully"
else
    print_error "Failed to delete organization (HTTP $HTTP_CODE)"
fi

# Verify deletion
print_step "STEP 6" "Verifying organization deletion"
VERIFY_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL/org/get?organization_name=$ORG_NAME")
VERIFY_HTTP_CODE=$(echo "$VERIFY_RESPONSE" | tail -n1)

if [ "$VERIFY_HTTP_CODE" == "404" ]; then
    print_success "Deletion verified - organization no longer exists"
else
    print_error "Organization still exists after deletion"
fi

# Final Summary
echo ""
echo "=========================================="
echo "${GREEN}  ALL SMOKE TESTS PASSED!${NC}"
echo "=========================================="
echo ""
echo "Summary:"
echo "  ✓ Organization creation"
echo "  ✓ Admin authentication (JWT)"
echo "  ✓ Organization retrieval"
echo "  ✓ Organization update (with collection migration)"
echo "  ✓ Organization deletion"
echo "  ✓ Data cleanup verification"
echo ""
echo "[INFO] The Croupier API is fully functional!"
echo ""

exit 0
