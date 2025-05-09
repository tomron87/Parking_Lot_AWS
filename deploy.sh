#!/bin/bash

# Build the application
sam build

# Deploy the application
sam deploy --guided