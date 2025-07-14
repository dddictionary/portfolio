#!/bin/bash

API_BASE_URL="http://localhost:5000/api/timeline_post"

UNIQUE_SUFFIX=$(date +%s)
TEST_CONTENT="Simple test post content - $UNIQUE_SUFFIX"
TEST_EMAIL="testuser-$UNIQUE_SUFFIX@example.com"
TEST_NAME="Test User $UNIQUE_SUFFIX"

echo "Generated unique content: '$TEST_CONTENT'"
echo "Generated unique email: '$TEST_EMAIL'"
echo "Generated unique name: '$TEST_NAME'"

echo -e "\nSending POST request to create a new post..."
POST_RESPONSE=$(curl -X POST -d  'name='"$TEST_NAME"'&email='"$TEST_EMAIL"'&content='"$TEST_CONTENT"'' "$API_BASE_URL")

echo -e "\nPOST Response: $POST_RESPONSE"

POST_ID=$(echo "$POST_RESPONSE" | jq -r '.id' 2>/dev/null)

if [ -z "$POST_ID" ] || [ "$POST_ID" == "null" ]; then
    echo "ERROR: Failed to extract post ID from POST response. Cannot proceed with verification/deletion."
    exit 1
fi

echo -e "\nSuccessfully created post with ID: $POST_ID"

echo -e "\nSending GET request to retrieve all posts..."
GET_RESPONSE=$(curl -s "$API_BASE_URL")

echo "GET Response (first 500 chars): ${GET_RESPONSE:0:500}..."

echo -e "\nVerifying the new post in GET response..."
if echo "$GET_RESPONSE" | grep -q "$TEST_CONTENT"; then
    echo "VERIFICATION SUCCESS: Found '$TEST_CONTENT' in the GET response."
else
    echo "VERIFICATION FAILED: Could not find '$TEST_CONTENT' in the GET response."
    exit 1
fi

# TODO: Add a delete endpoint and test for that here.
