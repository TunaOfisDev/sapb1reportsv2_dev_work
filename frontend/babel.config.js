module.exports = {
  presets: [
    [
      '@babel/preset-env',
      {
        targets: {
          node: 'current',
          browsers: 'defaults and not IE 11'
        },
      },
    ],
    '@babel/preset-react',
  ],
  plugins: [
    '@babel/plugin-transform-runtime',
    ['@babel/plugin-proposal-private-property-in-object', { loose: false }],
    '@babel/plugin-syntax-dynamic-import',
    ['@babel/plugin-proposal-class-properties', { loose: false }],
    'babel-plugin-styled-components'
  ],
  cacheDirectory: true,
  cacheCompression: false,
};