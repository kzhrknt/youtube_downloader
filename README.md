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

アプリケーションは「Sign in to confirm you're not a bot」エラーを回避するために強化されています。

内部的には以下の機能が実装されています：
- AndroidモバイルクライアントをエミュレートしてYouTubeにアクセス
- YouTube APIのチェックをスキップする高度な設定
- 適切なリファラーとユーザーエージェントを使用

もしそれでもエラーが表示される場合：
1. 最新バージョンのyt-dlp (2024.4.9以降) を使用していることを確認
2. 以下のコマンドでyt-dlpを更新：
   ```
   pip install -U yt-dlp
   ```
3. VPNを使用している場合は一時的に無効化してみる

問題が解決しない場合、一時的な対策としてブラウザでURLを開いて視聴してからアプリを使用することで回避できることがあります。

### HTTP 416 エラー対策

高画質ダウンロード時に「HTTP Error 416: Requested range not satisfiable」というエラーが表示される場合は、内部的に以下の対策が施されています：

- チャンクサイズの調整（10MB単位でのダウンロード）
- 複数回の再試行処理
- 代替フォーマットへのフォールバック

それでもエラーが発生する場合は、通常モードでのダウンロードをお試しください。

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