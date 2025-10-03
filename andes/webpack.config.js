// webpack.config.js (versión recomendada)
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin   = require("css-minimizer-webpack-plugin");
const { SourceMapDevToolPlugin } = require("webpack");
const path = require('path');

module.exports = {
  entry: {
    main: './static/assets/index.js',   // único entry: importa el CSS desde index.js
  },
  output: {
    filename: '[name].bundle.js',       // -> main.bundle.js
    path: path.resolve(__dirname, 'static/dist/'),
    publicPath: '/static/dist/',
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: [
          MiniCssExtractPlugin.loader,
          'css-loader',
          'postcss-loader'
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
  plugins: [
    new MiniCssExtractPlugin({
      filename: '[name].css'   // -> main.css
    }),
    new SourceMapDevToolPlugin({ filename: "[file].map" })
  ],
  optimization: {
    minimizer: [ new CssMinimizerPlugin() ]
  },
};
