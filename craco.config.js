const CracoEsbuildPlugin = require('craco-esbuild');

module.exports = {
 webpack: {
   configure: (webpackConfig) => {
     webpackConfig.optimization = {
       ...webpackConfig.optimization,
       splitChunks: {
         chunks: 'all',
         minSize: 10000,
         maxSize: 250000,
       },
       runtimeChunk: true
     };
     // Kaynak haritaları etkinleştiriliyor
     webpackConfig.devtool = 'source-map';
     
     // React için fallback ekle
     webpackConfig.resolve = {
       ...webpackConfig.resolve,
       fallback: {
         ...webpackConfig.resolve?.fallback,
         "react": require.resolve("react"),
         "react-dom": require.resolve("react-dom")
       }
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
         target: 'es2020',
         loader: 'jsx',
         sourcemap: true,
         jsxFactory: 'React.createElement',
         jsxFragment: 'React.Fragment',
         jsx: 'automatic'
       },
       esbuildMinimizerOptions: {
         target: 'es2020',
         sourcemap: true,
         css: true,
         jsx: 'automatic',
         jsxFactory: 'React.createElement',
         jsxFragment: 'React.Fragment'
       },
       skipEsbuildJest: true
     },
   },
 ],
 babel: {
   presets: [
     [
       '@babel/preset-react',
       {
         runtime: 'automatic'
       }
     ]
   ]
 }
};