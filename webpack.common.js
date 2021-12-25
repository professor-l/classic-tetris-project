const path = require('path')
const webpack = require('webpack')
const BundleTracker = require('webpack-bundle-tracker')
const MiniCssExtractPlugin = require('mini-css-extract-plugin');

const devMode = process.env.NODE_ENV !== 'production';

module.exports = {
  context: __dirname,

  entry: './classic_tetris_project/private/assets/app',

  output: {
    path: path.resolve('./static/bundles/'),
    filename: '[name]-[hash].js',
  },

  plugins: [
    new BundleTracker({
      path: __dirname,
      filename: './webpack-stats.json',
    }),
    new MiniCssExtractPlugin({
      filename: '[name]-[hash].css',
    }),
    new webpack.HotModuleReplacementPlugin(),

    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery"
    }),
  ],

  module: {
    rules: [
      { test: /\.scss/, use: [MiniCssExtractPlugin.loader, 'css-loader', 'sass-loader' ], },
      {
        test: require.resolve('jquery'),
        loader: 'expose-loader',
        options: {
          exposes: ['$', 'jQuery'],
        },
      },
    ],
  },

  resolve: {
    modules: ['node_modules'],
    extensions: ['.js']
  },
}
