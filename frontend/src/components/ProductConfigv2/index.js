// frontend/src/components/ProductConfigv2/index.js

// API servisleri
import configApi from './api/configApi';

// Contextler
import { ProductConfigProvider } from './contexts/ProductConfigContext';
import { RuleProvider } from './contexts/RuleContext';

// Hook'lar
import useConfigurator from './hooks/useConfigurator';
import useRuleEngine from './hooks/useRuleEngine';

// Sayfalar (Pages)
import VariantListPage from './pages/VariantListPage'; 

// Konfigüratör bileşenleri
import ConfiguratorMain from './components/Configurator/ConfiguratorMain';
import FeatureSection from './components/Configurator/FeatureSection';
import OptionSelector from './components/Configurator/OptionSelector';
import ProductVisualization from './components/Configurator/ProductVisualization';
import PriceSummary from './components/Configurator/PriceSummary';
import RuleFeedback from './components/Configurator/RuleFeedback';

// Admin bileşenleri
import RuleEditor from './components/Admin/RuleEditor';
import ProductManager from './components/Admin/ProductManager';

// Paylaşılan bileşenler
import FeatureCard from './components/Shared/FeatureCard';
import OptionButton from './components/Shared/OptionButton';
import ProductCard from './components/Shared/ProductCard';

// Tüm modülü dışa aktarma (named ve default export)
export {
  configApi,
  ProductConfigProvider,
  RuleProvider,
  useConfigurator,
  useRuleEngine,
  VariantListPage,
  ConfiguratorMain,
  FeatureSection,
  OptionSelector,
  ProductVisualization,
  PriceSummary,
  RuleFeedback,
  RuleEditor,
  ProductManager,
  FeatureCard,
  OptionButton,
  ProductCard,
};

export default {
  configApi,
  ProductConfigProvider,
  RuleProvider,
  useConfigurator,
  useRuleEngine,
  VariantListPage,
  ConfiguratorMain,
  FeatureSection,
  OptionSelector,
  ProductVisualization,
  PriceSummary,
  RuleFeedback,
  RuleEditor,
  ProductManager,
  FeatureCard,
  OptionButton,
  ProductCard,
};
