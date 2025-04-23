#!/bin/bash
# YouTube Downloader インストールガイドを開くスクリプト

# スクリプトが実行されているディレクトリをカレントディレクトリに設定
cd "$(dirname "$0")"

# HTMLファイルの絶対パスを取得
GUIDE_PATH="$(pwd)/index.html"

# ブラウザでガイドを開く
echo "YouTube Downloader インストールガイドを開いています..."
open "$GUIDE_PATH"

echo "インストールガイドがブラウザで開かれました。"
echo "このウィンドウは閉じて構いません。"