#!/bin/bash
# /var/www/sapb1reportsv2/frontend/src/components/ProductConfigv2 dizin yapısını oluşturur

BASE_DIR="/var/www/sapb1reportsv2/frontend/src/components/ProductConfigv2"

# Alt dizinleri oluştur
mkdir -p "$BASE_DIR/api"
mkdir -p "$BASE_DIR/components/Configurator"
mkdir -p "$BASE_DIR/components/Admin"
mkdir -p "$BASE_DIR/components/Shared"
mkdir -p "$BASE_DIR/contexts"
mkdir -p "$BASE_DIR/hooks"
mkdir -p "$BASE_DIR/rules"
mkdir -p "$BASE_DIR/styles"
mkdir -p "$BASE_DIR/utils"

# Dosyaları oluştur
touch "$BASE_DIR/api/configApi.js"

touch "$BASE_DIR/components/Configurator/ConfiguratorMain.js"
touch "$BASE_DIR/components/Configurator/FeatureSection.js"
touch "$BASE_DIR/components/Configurator/OptionSelector.js"
touch "$BASE_DIR/components/Configurator/ProductVisualization.js"
touch "$BASE_DIR/components/Configurator/PriceSummary.js"
touch "$BASE_DIR/components/Configurator/RuleFeedback.js"

touch "$BASE_DIR/components/Admin/RuleEditor.js"
touch "$BASE_DIR/components/Admin/ProductManager.js"

touch "$BASE_DIR/components/Shared/ProductCard.js"
touch "$BASE_DIR/components/Shared/FeatureCard.js"
touch "$BASE_DIR/components/Shared/OptionButton.js"

touch "$BASE_DIR/contexts/ProductConfigContext.js"
touch "$BASE_DIR/contexts/RuleContext.js"

touch "$BASE_DIR/hooks/useConfigurator.js"
touch "$BASE_DIR/hooks/useRuleEngine.js"

touch "$BASE_DIR/rules/RuleValidator.js"

touch "$BASE_DIR/styles/configurator.css"
touch "$BASE_DIR/styles/_product-config.scss"

touch "$BASE_DIR/utils/configHelpers.js"
touch "$BASE_DIR/utils/priceCalculator.js"

touch "$BASE_DIR/index.js"
