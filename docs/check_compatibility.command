#!/bin/bash
# YouTube Downloader 互換性チェックスクリプト

echo "YouTube Downloaderシステム互換性チェック"
echo "======================================="
echo ""

# macOSのバージョンをチェック
OS_VERSION=$(sw_vers -productVersion)
echo "macOSバージョン: $OS_VERSION"

# macOS 10.13以上が望ましい
if [[ "$(sw_vers -productVersion | cut -d. -f2)" -lt 13 && "$(sw_vers -productVersion | cut -d. -f1)" -eq 10 ]]; then
  echo "警告: macOS 10.13 (High Sierra)以上を推奨します。"
  echo "現在のバージョン: $OS_VERSION"
  echo ""
else
  echo "✓ macOSバージョンは互換性があります"
  echo ""
fi

# FFmpegのインストール状況をチェック
echo "FFmpegのチェック中..."
if command -v ffmpeg >/dev/null 2>&1; then
  FFMPEG_VERSION=$(ffmpeg -version | head -n1)
  echo "✓ FFmpegが見つかりました: $FFMPEG_VERSION"
  echo ""
else
  echo "警告: FFmpegがインストールされていません。"
  echo "高画質モードを使用するにはFFmpegが必要です。"
  echo "インストール方法: brew install ffmpeg"
  echo ""
fi

# 空きディスク容量をチェック
DISK_SPACE=$(df -h / | awk 'NR==2 {print $4}')
echo "空きディスク容量: $DISK_SPACE"
DISK_SPACE_MB=$(df -m / | awk 'NR==2 {print $4}')

if [[ $DISK_SPACE_MB -lt 1000 ]]; then
  echo "警告: 空きディスク容量が少なめです。動画のダウンロードには十分な空き容量が必要です。"
  echo ""
else
  echo "✓ ディスク容量は十分です"
  echo ""
fi

# インターネット接続をチェック
echo "インターネット接続のチェック中..."
if ping -c 1 youtube.com >/dev/null 2>&1; then
  echo "✓ インターネット接続は正常です"
  echo ""
else
  echo "警告: インターネット接続に問題があるようです。"
  echo "YouTube Downloaderを使用するには安定したインターネット接続が必要です。"
  echo ""
fi

echo "互換性チェック完了"
echo "問題が報告された場合は、それらを解決してからYouTube Downloaderを使用してください。"
echo ""
echo "エンターキーを押して終了..."
read