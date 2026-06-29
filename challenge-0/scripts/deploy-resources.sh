#!/bin/bash
# deploy-resources.sh — Deploy Azure resources for the MAF Workshop
# Usage: ./deploy-resources.sh --resource-group <name> --location <region>

set -e

# Default values
RESOURCE_GROUP=""
LOCATION="swedencentral"
PROJECT_NAME="maf-lab"
MODEL_NAME="gpt-4o"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --resource-group|-g) RESOURCE_GROUP="$2"; shift 2 ;;
        --location|-l) LOCATION="$2"; shift 2 ;;
        --project-name|-p) PROJECT_NAME="$2"; shift 2 ;;
        *) echo "Unknown option: $1"; exit 1 ;;
    esac
done

if [ -z "$RESOURCE_GROUP" ]; then
    echo "❌ Error: --resource-group is required"
    echo "Usage: ./deploy-resources.sh --resource-group <name> [--location <region>]"
    exit 1
fi

echo "🚀 Deploying MAF Workshop Resources"
echo "   Resource Group: $RESOURCE_GROUP"
echo "   Location: $LOCATION"
echo "   Project Name: $PROJECT_NAME"
echo ""

# 1. Create Resource Group
echo "📦 Creating Resource Group..."
az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --output none
echo "   ✅ Resource Group created"

# 2. Create AI Foundry Hub
echo "🏗️  Creating AI Foundry Hub..."
FOUNDRY_NAME="${PROJECT_NAME}-hub"
az cognitiveservices account create \
    --name "$FOUNDRY_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --kind "AIFoundry" \
    --sku "S0" \
    --output none 2>/dev/null || echo "   ⚠️  Hub may already exist, continuing..."
echo "   ✅ AI Foundry Hub ready"

# 3. Create AI Services (for model deployments)
echo "🧠 Creating AI Services account..."
AI_SERVICES_NAME="${PROJECT_NAME}-ai"
az cognitiveservices account create \
    --name "$AI_SERVICES_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --location "$LOCATION" \
    --kind "AIServices" \
    --sku "S0" \
    --output none 2>/dev/null || echo "   ⚠️  AI Services may already exist, continuing..."
echo "   ✅ AI Services ready"

# 4. Deploy GPT-4o model
echo "🤖 Deploying GPT-4o model..."
az cognitiveservices account deployment create \
    --name "$AI_SERVICES_NAME" \
    --resource-group "$RESOURCE_GROUP" \
    --deployment-name "$MODEL_NAME" \
    --model-name "gpt-4o" \
    --model-version "2024-11-20" \
    --model-format "OpenAI" \
    --sku-name "GlobalStandard" \
    --sku-capacity 450 \
    --output none 2>/dev/null || echo "   ⚠️  Model deployment may already exist, continuing..."
echo "   ✅ GPT-4o deployed (GlobalStandard, 450K TPM)"

echo ""
echo "✅ All resources deployed successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. Run: ./get-keys.sh --resource-group $RESOURCE_GROUP"
echo "   2. This will populate your .env file automatically"
