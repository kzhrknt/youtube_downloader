#!/bin/bash
# YouTube Downloaderを起動するスクリプト

echo "YouTube Downloaderを起動しています..."

# アプリが存在するか確認
if [ -d "/Applications/YouTube Downloader.app" ]; then
    # アプリケーションフォルダにある場合
    open "/Applications/YouTube Downloader.app"
    echo "YouTube Downloaderが起動しました。このウィンドウは閉じて構いません。"
elif [ -d "$HOME/Applications/YouTube Downloader.app" ]; then
    # ユーザーのアプリケーションフォルダにある場合
    open "$HOME/Applications/YouTube Downloader.app"
    echo "YouTube Downloaderが起動しました。このウィンドウは閉じて構いません。"
elif [ -d "./YouTube Downloader.app" ]; then
    # カレントディレクトリにある場合
    open "./YouTube Downloader.app"
    echo "YouTube Downloaderが起動しました。このウィンドウは閉じて構いません。"
else
    # アプリが見つからない場合
    echo "エラー: YouTube Downloaderアプリが見つかりません。"
    echo "インストールが正常に完了していない可能性があります。"
    echo "インストールガイドの手順に従って再インストールしてください。"
    echo ""
    echo "Enterキーを押して終了..."
    read
fi