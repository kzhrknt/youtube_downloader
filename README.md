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

## エラー対策

問題が発生した場合:

1. 最新バージョンのyt-dlp (2024.4.9以降) を使用していることを確認:
   ```
   pip install -U yt-dlp
   ```

2. 高画質モードに問題がある場合は通常モードでのダウンロードをお試しください

3. 別の動画でテストしてみてください

4. 「Sign in to confirm you're not a bot」エラーが表示される場合:
   - ブラウザで同じURLを開いて視聴してから再度試す
   - VPNを使用している場合は一時的に無効化する

シンプルで安定したコードを使用しているため、ほとんどの動画で問題なくダウンロードできるはずです。

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