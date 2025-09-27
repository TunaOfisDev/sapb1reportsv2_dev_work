const fs = require('fs').promises;
const path = require('path');
const { execSync } = require('child_process');
const glob = require('glob');

async function setupProject() {
  try {
    console.log('Proje kurulumu başlatılıyor...');

    // Yollar
    const projectRoot = path.resolve(__dirname, '..');
    const packageJsonPath = path.join(projectRoot, 'package.json');
    const cracoConfigPath = path.join(projectRoot, 'craco.config.js');
    const eslintConfigPath = path.join(projectRoot, '.eslintrc.json');
    const cacheDir = path.join(projectRoot, '.npm-cache');
    const nodeModulesDir = path.join(projectRoot, 'node_modules');
    const srcDir = path.join(projectRoot, 'src');

    // package.json oku
    const packageJson = JSON.parse(await fs.readFile(packageJsonPath, 'utf-8'));
    const dependencies = {
      ...packageJson.dependencies,
      ...packageJson.devDependencies,
    };

    // Gerekli bağımlılıklar (craco.config.js ve bilinen ihtiyaçlar)
    const requiredDeps = [
      'eslint-webpack-plugin',
      'craco-esbuild',
      'eslint',
      'react-toastify',
      '@babel/preset-react',
      '@reduxjs/toolkit',
      '@fortawesome/free-solid-svg-icons',
      '@fortawesome/react-fontawesome',
      '@mui/icons-material', // Yeni eklendi
    ];

    // Kaynak kodda kullanılan bağımlılıkları tara
    const sourceFiles = glob.sync('**/*.{js,jsx,ts,tsx}', { cwd: srcDir });
    const detectedDeps = new Set();
    for (const file of sourceFiles) {
      const content = await fs.readFile(path.join(srcDir, file), 'utf-8');
      const matches = content.match(/(?:from\s+['"]([^'"]+)['"]|require\(['"]([^'"]+)['"]\))/g) || [];
      matches.forEach((match) => {
        const dep = match.match(/['"]([^'"]+)['"]/)[1];
        // Tam paket isimlerini al (kapsamlı veya normal)
        if (!dep.startsWith('.')) {
          detectedDeps.add(dep);
        }
      });
    }

    // Eksik bağımlılıkları kontrol et
    const missingDeps = [...requiredDeps, ...detectedDeps].filter(
      (dep) => !dependencies[dep] && !dep.startsWith('@')
    );
    if (missingDeps.length > 0) {
      console.log('Eksik bağımlılıklar:', missingDeps);
      console.log('Eksik bağımlılıklar kuruluyor...');
      execSync(`npm install ${missingDeps.join(' ')}`, { stdio: 'inherit' });
    } else {
      console.log('Tüm gerekli bağımlılıklar package.json içinde mevcut.');
    }

    // ESLint yapılandırmasını kontrol et
    try {
      await fs.access(eslintConfigPath);
      console.log('.eslintrc.json bulundu.');
    } catch {
      console.log('.eslintrc.json bulunamadı, oluşturuluyor...');
      const eslintConfig = {
        env: { browser: true, es2021: true, jest: true },
        extends: [
          'eslint:recommended',
          'plugin:react/recommended',
          'plugin:react-hooks/recommended',
          'plugin:@mui/recommended', // MUI için
        ],
        parserOptions: { ecmaVersion: 12, sourceType: 'module', ecmaFeatures: { jsx: true } },
        plugins: ['react', 'react-hooks', '@mui'], // MUI için
        rules: { 'react/prop-types': 'off', 'react/react-in-jsx-scope': 'off' },
        settings: { react: { version: 'detect' } },
      };
      await fs.writeFile(eslintConfigPath, JSON.stringify(eslintConfig, null, 2));
      console.log('.eslintrc.json oluşturuldu.');
    }

    // Önbellekleri temizle
    console.log('Önbellekler temizleniyor...');
    try {
      await fs.rm(cacheDir, { recursive: true, force: true });
      await fs.rm(nodeModulesDir, { recursive: true, force: true });
      console.log('Önbellekler temizlendi.');
    } catch (err) {
      console.warn('Önbellek bulunamadı veya temizlenemedi:', err.message);
    }

    // Tüm bağımlılıkları kur
    console.log('npm install çalıştırılıyor...');
    execSync('npm install', { stdio: 'inherit', cwd: projectRoot });

    // Kurulumu doğrula
    console.log('Kurulum build ile doğrulanıyor...');
    try {
      execSync('npm run build', { stdio: 'inherit', cwd: projectRoot });
      console.log('Build başarılı! Proje kurulumu tamamlandı.');
    } catch (err) {
      console.error('Build başarısız. Yukarıdaki hata çıktısını kontrol edin.');
      process.exit(1);
    }

  } catch (err) {
    console.error('Kurulum başarısız:', err.message);
    process.exit(1);
  }
}

setupProject();