#!/bin/bash
# ================================================================================
# File: apply.sh
#
# Purpose:
#   End-to-end deployment of the Cost Explorer MCP stack. Provisions the six cost
#   Lambdas, the MCP router Lambda, the Cognito identity layer, the OAuth state
#   table, and the HTTP API. validate.sh prints the MCP endpoint at the end;
#   connecting Claude or ChatGPT to it is covered in the README.
# ================================================================================

# Default AWS region for all CLI and Terraform operations.
export AWS_DEFAULT_REGION="us-east-1"

# Strict shell: exit on error, error on unset vars, fail on any pipe stage.
set -euo pipefail

# ------------------------------------------------------------------------------
# Environment pre-check
# ------------------------------------------------------------------------------

echo "NOTE: Running environment validation..."
./check_env.sh

# ------------------------------------------------------------------------------
# Build Lambdas, Cognito, DynamoDB, and API Gateway
# ------------------------------------------------------------------------------

echo "NOTE: Building Lambdas, Cognito, and API Gateway..."

cd 01-lambdas || {
  echo "ERROR: 01-lambdas directory missing."
  exit 1
}

terraform init
terraform apply -auto-approve

cd .. || exit

# ------------------------------------------------------------------------------
# Post-deployment validation
# ------------------------------------------------------------------------------

# Direct-invokes each cost Lambda to confirm Cost Explorer connectivity.
echo "NOTE: Running build validation..."
./validate.sh

# ================================================================================
# End of script
# ================================================================================
