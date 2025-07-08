module.exports = {
    transform: {
      '^.+\\.(js|jsx|mjs|cjs|ts|tsx)$': 'babel-jest', // Babel ile dönüştürme işlemi
    },
    transformIgnorePatterns: [
      '/node_modules/(?!(axios)/)', // Axios ve diğer modülleri dahil etmek için
    ],
    moduleNameMapper: {
      '\\.(css|less|scss|sass)$': 'identity-obj-proxy', // Stil dosyalarını mocklamak için
    },
    testEnvironment: 'jsdom', // React bileşenlerini test etmek için
  };
  