#!/bin/bash
docker run --name test-maddash-token --rm \
  --network=host \
  --env auth_secret=secret wipac/token-service:latest python test_server.py # &