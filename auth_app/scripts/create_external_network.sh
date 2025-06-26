#!/bin/bash
NETWORK_NAME="app_network"
echo "check if docker network '$NETWORK_NAME' exists"

if docker network inspect "$NETWORK_NAME" > /dev/null 2>&1; then
  echo "Network: '$NETWORK_NAME' already exists"
else
  echo "Creating network: '$NETWORK_NAME'"
  docker network create "$NETWORK_NAME"
  echo "Network '$NETWORK_NAME' created"
fi
