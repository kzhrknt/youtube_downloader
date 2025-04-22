# YouTube Downloader

YouTubeの動画を簡単にダウンロードするためのアプリケーションです。

## 特徴

- 様々な品質・形式での動画ダウンロード
- 高画質ダウンロードモード（動画と音声を別々にダウンロードして結合）
- シンプルで使いやすいグラフィカルインターフェース
- reCAPTCHAによるボット検出の回避機能

## インストール方法

### 方法1: pipを使用してインストール

```bash
pip install git+https://github.com/kzhrknt/youtube_downloader.git
```

### 方法2: ソースからインストール

```bash
git clone https://github.com/kzhrknt/youtube_downloader.git
cd youtube_downloader
pip install -e .
```

## 依存関係

- Python 3.6以上
- PyQt5
- yt-dlp
- FFmpeg (高画質モード使用時に必要)

### FFmpegのインストール

#### Windows
1. [FFmpeg公式サイト](https://ffmpeg.org/download.html)からダウンロード
2. 解凍したフォルダをCドライブ直下に配置
3. 環境変数のPATHに「C:\ffmpeg\bin」を追加

#### macOS
```bash
brew install ffmpeg
```

#### Linux (Ubuntu)
```bash
sudo apt update
sudo apt install ffmpeg
```

## 「ボット検出」エラーへの対処法

アプリを使用中に「Sign in to confirm you're not a bot」というエラーが表示される場合は、以下の方法で対処できます：

1. ブラウザでYouTubeにログイン
2. ブラウザから同じURLにアクセスして1回再生する
3. アプリを再起動し、再度お試しください

内部的には以下の機能が実装されています：
- ブラウザのCookie情報を使用して認証情報を共有
- モバイルクライアントとしてアクセスしてbot検出を回避

## 使い方

1. アプリケーションを起動します：
```bash
youtube-downloader
```

2. YouTubeのURLを入力して「情報取得」ボタンをクリックします
3. ダウンロードする形式を選択するか、高画質モードのチェックボックスをオンにします
4. 「ダウンロード」ボタンをクリックします
5. ダウンロードが完了すると通知が表示されます

## ライセンス

MITライセンス