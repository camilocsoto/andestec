// webpack.config.js
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin   = require("css-minimizer-webpack-plugin");
const { SourceMapDevToolPlugin } = require("webpack");
const path = require('path');

module.exports = {
  // Definimos dos bundles: uno JS+CSS, y otro solo Tailwind
  entry: {
    main:   './static/assets/index.js',   // tu app JS + imports CSS
    output: './static/assets/style.css',  // solo Tailwind input
  },
  output: {
    filename: '[name].bundle.js',         // genera main.bundle.js y output.bundle.js (vacío)
    path: path.resolve(__dirname, 'static/dist/')
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          'postcss-loader'  // lee tailwind.config.js
        ],
      },
      {
        test: /\.(png|jpg|gif|svg)$/,
        type: 'asset/resource',
        generator: { filename: 'images/[name][ext]' }
      },
      {
        test: /\.(ttf|eot|woff2?|svg)$/,
        type: 'asset/resource'
      },
    ],
  },
  resolve: { extensions: ['.js', '.css'] },
  plugins: [
    new MiniCssExtractPlugin({
      filename: '[name].css'  // creará main.css y output.css
    }),
    new SourceMapDevToolPlugin({ filename: "[file].map" })
  ],
  optimization: {
    minimizer: [ new CssMinimizerPlugin() ]
  },
};

/**
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin   = require("css-minimizer-webpack-plugin");
const { SourceMapDevToolPlugin } = require("webpack");
const path = require('path');

module.exports = {
  // Definimos dos bundles: uno JS+CSS, y otro solo Tailwind
  entry: {
    main:   './static/assets/index.js',   // tu app JS + imports CSS
  },
  output: {
    filename: '[name].bundle.js',         // genera main.bundle.js y output.bundle.js (vacío)
    path: path.resolve(__dirname, 'static/dist/'),
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          'postcss-loader'  // lee tailwind.config.js
        ],
      },
      {
        test: /\.(png|jpg|gif|svg)$/,
        type: 'asset/resource',
        generator: { filename: 'images/[name][ext]' }
      },
      {
        test: /\.(ttf|eot|woff2?|svg)$/,
        type: 'asset/resource'
      },
    ],
  },
  resolve: { extensions: ['.js', '.css'] },
  plugins: [
    new MiniCssExtractPlugin({
      filename: '[name].css'  // creará main.css y output.css
    }),
    new SourceMapDevToolPlugin({ filename: "[file].map" })
  ],
  optimization: {
    minimizer: [ new CssMinimizerPlugin() ]
  },
};
*/