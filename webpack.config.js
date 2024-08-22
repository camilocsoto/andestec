const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const { SourceMapDevToolPlugin } = require("webpack");
const path = require('path');

module.exports = {
  entry: './andes/interface/static/assets/index.js', // Punto de entrada para tu JS
  output: {
    filename: '[name].bundle.js',
    path: path.resolve(__dirname, './andes/interface/static/dist/')
  },
  module: {
    rules: [
      {
        test: /\.css$/,
        use: ['style-loader', 'css-loader', 'postcss-loader'],
      },
      {
        test: /\.(png|jpg|gif|svg)$/,
        loader: 'file-loader',
        options: {
            outputPath: 'images/'
        }
      },
      {
        test: /\.(ttf|eot|svg|gif|woff|woff2)(\?v=[0-9]\.[0-9]\.[0-9])?$/,
        use: [{
            loader: 'file-loader',
        }]
      },      
    ],
  },
  resolve: {
    extensions: ['.js', '.jsx', '.css'],
},
plugins: [
    new MiniCssExtractPlugin(),
    new SourceMapDevToolPlugin({
        filename: "[file].map"
    })
],
optimization: {
    minimizer: [
        new CssMinimizerPlugin()
    ]
},
};