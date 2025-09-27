Webpack + Babel'den Esbuild'e Geçiş (Hızlı Build İçin)
Babel yerine esbuild kullanarak React uygulamanın build süresini 5-10 kata kadar hızlandırabilirsin. Bunu yapmak için Babel bağımlılıklarını kaldırıp, esbuild-loader kullanacağız.

1. Gereksiz Babel Yapılarını Temizleme
Babel artık kullanılmayacağı için, ilgili dosya ve bağımlılıkları kaldırmalıyız.

Aşağıdaki dosyaları sil:
rm -f frontend/.babelrc
rm -f frontend/babel.config.js

Aşağıdaki Babel bağımlılıklarını kaldır:
npm remove @babel/core @babel/preset-env @babel/preset-react babel-loader

Bu adımlarla Babel tamamen kaldırıldı.

2. Esbuild ve Craco'yu Yükleme
React-Scripts'in Webpack yapılandırmasını değiştirmek için Craco kullanacağız ve Esbuild'i devreye alacağız.

Gerekli bağımlılıkları yükle:
npm install --save-dev @craco/craco craco-esbuild esbuild esbuild-loader

Bu, Esbuild ile Craco'yu projene entegre edecek.

3. package.json Güncelleme
Artık Babel yerine Esbuild kullanacağız, bu yüzden react-scripts yerine craco kullanmalıyız.

package.json içinde aşağıdaki değişiklikleri yap:

Bul:
"scripts": {
  "start": "react-scripts start",
  "build": "react-scripts build",
  "test": "react-scripts test"
}

Şununla değiştir:
"scripts": {
  "start": "craco start",
  "build": "craco build",
  "test": "craco test"
}

Böylece artık Craco ve Esbuild ile build yapacağız.

4. craco.config.js Dosyası Oluşturma
Craco'yu Esbuild ile çalışacak şekilde ayarlayacağız.

frontend/craco.config.js oluştur ve içine şunu ekle:
const CracoEsbuildPlugin = require('craco-esbuild');

module.exports = {
  webpack: {
    configure: (webpackConfig) => {
      webpackConfig.optimization.splitChunks = {
        chunks: 'all',
        minSize: 20000,
        maxSize: 500000,
      };
      return webpackConfig;
    },
  },
  plugins: [
    {
      plugin: CracoEsbuildPlugin,
      options: {
        enableSvgr: true,
        esbuildLoaderOptions: {
          target: 'es2015',
          loader: 'jsx',
        },
        esbuildMinimizerOptions: {
          target: 'es2015',
        },
        skipEsbuildJest: false,
      },
    },
  ],
};

Bu, Esbuild'in Webpack ile uyumlu şekilde çalışmasını sağlayacak.

5. Eski Build ve Cache'leri Temizleme
Önceki Babel yapılandırmalarının build sürecini etkilememesi için eski cache ve build dosyalarını temizleyelim.

Terminalde şu komutları çalıştır:
rm -rf build node_modules/.cache && npm cache clean --force

Böylece eski Babel cache'leri temizlenmiş olacak.

6. Yeni Build Çalıştırma ve Test Etme
Her şey hazır, artık build alıp hız farkını ölçelim!

Yeni build al:
npm run build

Build süresini ölçmek için:
time npm run build

Esbuild sayesinde build süresi önemli ölçüde kısalacaktır.

Zombie (defunct) Node.js Süreçlerini Temizleyelim
Zombie süreçler performansı olumsuz etkileyebilir, bu yüzden temizleyelim.

1. Ebeveyn Süreçleri Öldür
Tüm zombie süreçleri öldürmek için:
ps -eo pid,ppid,cmd | grep '[n]ode' | awk '{print $2}' | sort -u | xargs -I {} kill -9 {}

Bu, tüm zombie süreçlerin ebeveynlerini öldürecektir.

2. Zombie Süreçlerin Temizlendiğini Kontrol Et
Süreçlerin temizlenip temizlenmediğini kontrol etmek için:
ps aux | grep node

Eğer defunct süreçler artık listede görünmüyorsa, temizleme işlemi başarılı olmuştur.

3. Node.js İşlemlerini Yeniden Başlat (Gerekirse)
Eğer sistemde çalışan başka node süreçleri varsa, temizlemek için:
pkill -9 -f node

Sonrasında Node.js işlemlerini yeniden başlatmak için:
npm start

Böylece, Node.js süreçleri yeniden sağlıklı şekilde çalışacaktır.

4. Build İşlemini Tekrar Başlat
Şimdi temizlenmiş sistemle build işlemini tekrar çalıştırabilirsin:
npm run build

Zombie süreçler temizlendikten sonra build işleminin hızlandığını görebilirsin.

