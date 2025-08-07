#!/bin/bash

# Test script to validate Dockerfile syntax and build logic
echo "Testing Dockerfile syntax and build logic..."

# Test 1: Check if Dockerfile syntax is valid
echo "1. Checking Dockerfile syntax..."
docker build --dry-run . > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✓ Dockerfile syntax is valid"
else
    echo "✗ Dockerfile syntax error detected"
    exit 1
fi

# Test 2: Test build without token (should show appropriate message)
echo "2. Testing build without GitHub token..."
docker build --no-cache --progress=plain -t test-tdlib:no-token . 2>&1 | grep -q "Cloning TDLib repository without authentication"
if [ $? -eq 0 ]; then
    echo "✓ Build correctly handles missing token"
else
    echo "✗ Build does not handle missing token correctly"
fi

# Test 3: Test build with dummy token (will fail but should show token message)
echo "3. Testing build with GitHub token..."
docker build --no-cache --progress=plain --build-arg GITHUB_TOKEN=dummy_token -t test-tdlib:with-token . 2>&1 | grep -q "Cloning TDLib repository with token authentication"
if [ $? -eq 0 ]; then
    echo "✓ Build correctly handles provided token"
else
    echo "✗ Build does not handle provided token correctly"
fi

echo "Dockerfile testing completed!"
