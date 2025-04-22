import sys
import os
import re
import json
import time
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QComboBox, 
                             QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QWidget, QFileDialog, QProgressBar, QMessageBox, QGroupBox,
                             QCheckBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import yt_dlp

class VideoInfoThread(QThread):
    """動画情報を取得するスレッド"""
    info_signal = pyqtSignal(dict)
    error_signal = pyqtSignal(str)
    
    def __init__(self, url):
        super().__init__()
        self.url = url
        
    def run(self):
        try:
            # yt-dlp オプション
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'skip_download': True,
                # reCAPTCHA回避のためのオプション
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android'],  # AndroidクライアントとしてアクセスしてCAPTCHAを回避
                        'player_skip_youtubei_check': True,  # YouTubei APIチェックをスキップ
                    }
                },
                'referer': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',  # リファラーを設定
                'user_agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36',  # モバイルのユーザーエージェント
                'http_chunk_size': 10485760,  # チャンクサイズを10MBに設定（HTTP 416エラー対策）
                'format': 'best'  # 最高品質の形式を自動選択
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                
                if info:
                    self.info_signal.emit(info)
                else:
                    self.error_signal.emit("動画情報を取得できませんでした")
                    
        except Exception as e:
            self.error_signal.emit(f"情報取得に失敗しました: {str(e)}")


class DownloadThread(QThread):
    """動画をダウンロードするスレッド"""
    progress_signal = pyqtSignal(float, str)
    finished_signal = pyqtSignal(str)
    error_signal = pyqtSignal(str)
    
    def __init__(self, url, format_id, save_path, is_high_quality=False):
        super().__init__()
        self.url = url
        self.format_id = format_id
        self.save_path = save_path
        self.is_high_quality = is_high_quality
        
    def progress_hook(self, d):
        if d['status'] == 'downloading':
            if d.get('total_bytes'):
                # 進捗率を計算
                progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                # 速度表示
                speed = d.get('speed', 0)
                if speed:
                    speed_str = f"{speed/1024/1024:.2f} MB/s"
                else:
                    speed_str = "計算中..."
                
                self.progress_signal.emit(progress, speed_str)
            elif d.get('downloaded_bytes'):
                # サイズ不明の場合はダウンロード量だけ表示
                self.progress_signal.emit(-1, f"{d['downloaded_bytes']/1024/1024:.1f}MB ダウンロード済み")
                
        elif d['status'] == 'finished':
            self.progress_signal.emit(100, "処理中...")
        
    def run(self):
        try:
            if self.is_high_quality:
                # 高画質モード：動画と音声を別々にダウンロードして結合
                self.download_high_quality()
            else:
                # 通常モード：選択したフォーマットでダウンロード
                self.download_normal()
        except Exception as e:
            self.error_signal.emit(f"ダウンロード中にエラーが発生しました: {str(e)}")
    
    def download_normal(self):
        """通常のダウンロード処理"""
        filename = f"%(title)s.%(ext)s"
        output_path = os.path.join(self.save_path, filename)
        
        # yt-dlp オプション
        ydl_opts = {
            # 選択されたフォーマットIDがない場合はbestを使用
            'format': self.format_id if self.format_id else 'best',
            'outtmpl': output_path,
            'progress_hooks': [self.progress_hook],
            # reCAPTCHA回避のためのオプション
            'extractor_args': {
                'youtube': {
                    'player_client': ['android'],  # AndroidクライアントとしてアクセスしてCAPTCHAを回避
                    'player_skip_youtubei_check': True,  # YouTubei APIチェックをスキップ
                }
            },
            'referer': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',  # リファラーを設定
            'user_agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36',  # モバイルのユーザーエージェント
            'retries': 10,  # 再試行回数増加
            'fragment_retries': 10,  # フラグメントのダウンロード再試行回数
            'file_access_retries': 5,  # ファイルアクセスの再試行回数
            'extractor_retries': 5,  # 抽出器の再試行回数
            'http_chunk_size': 10485760,  # チャンクサイズを10MBに設定（HTTP 416エラー対策）
            'downloader_options': {'http_chunk_size': 10485760}  # ダウンローダーオプションにもチャンクサイズを設定
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(self.url, download=True)
            video_title = info_dict.get('title', '不明な動画')
            ext = info_dict.get('ext', 'mp4')
            out_filename = f"{video_title}.{ext}"
            
            self.finished_signal.emit(out_filename)
    
    def download_high_quality(self):
        """高画質モード：動画と音声を別々にダウンロードして結合"""
        # 一時ファイル名の設定
        temp_video_path = os.path.join(self.save_path, "temp_video.%(ext)s")
        temp_audio_path = os.path.join(self.save_path, "temp_audio.%(ext)s")
        
        # 高画質の動画のみをダウンロード（QuickTime互換性を考慮）
        self.progress_signal.emit(0, "高画質の動画をダウンロード中...")
        video_opts = {
            # QuickTimeで再生可能なフォーマットを指定（互換性向上）
            'format': 'bestvideo[ext=mp4][vcodec^=avc]/bestvideo/best',
            'outtmpl': temp_video_path,
            'progress_hooks': [self.progress_hook],
            'quiet': False,  # エラーメッセージを表示
            'no_warnings': False,  # 警告メッセージを表示
            'retries': 10,  # 再試行回数増加
            'fragment_retries': 10,  # フラグメントのダウンロード再試行回数
            'file_access_retries': 5,  # ファイルアクセスの再試行回数
            'extractor_retries': 5,  # 抽出器の再試行回数
        }
        
        try:
            # reCAPTCHA回避のための共通オプション
            captcha_options = {
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android'],  # AndroidクライアントとしてアクセスしてCAPTCHAを回避
                        'player_skip_youtubei_check': True,  # YouTubei APIチェックをスキップ
                    }
                },
                'referer': 'https://www.youtube.com/watch?v=dQw4w9WgXcQ',  # リファラーを設定
                'user_agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Mobile Safari/537.36',  # モバイルのユーザーエージェント
                'http_chunk_size': 10485760,  # チャンクサイズを10MBに設定（HTTP 416エラー対策）
                'downloader_options': {'http_chunk_size': 10485760},  # ダウンローダーオプションにもチャンクサイズを設定
            }
            
            # 動画オプションにreCAPTCHA回避オプションを追加
            video_opts.update(captcha_options)
            
            # 動画ファイルのダウンロード
            with yt_dlp.YoutubeDL(video_opts) as ydl:
                video_info = ydl.extract_info(self.url, download=True)
                video_filename = ydl.prepare_filename(video_info)
                
            # 最高音質の音声のみをダウンロード（Mac互換性を考慮）
            self.progress_signal.emit(0, "高音質の音声をダウンロード中...")
            audio_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio/best',  # m4aを優先、なければ最高音質、失敗時はbestを使用
                'outtmpl': temp_audio_path,
                'progress_hooks': [self.progress_hook],
                'quiet': False,  # エラーメッセージを表示
                'no_warnings': False,  # 警告メッセージを表示
                'retries': 10,  # 再試行回数増加
                'fragment_retries': 10,  # フラグメントのダウンロード再試行回数
                'file_access_retries': 5,  # ファイルアクセスの再試行回数
                'extractor_retries': 5,  # 抽出器の再試行回数
            }
            
            # 音声オプションにreCAPTCHA回避オプションを追加
            audio_opts.update(captcha_options)
            
            with yt_dlp.YoutubeDL(audio_opts) as ydl:
                audio_info = ydl.extract_info(self.url, download=True)
                audio_filename = ydl.prepare_filename(audio_info)
                
            # 最終的な出力ファイル名（安全な文字のみに置換）
            video_title = video_info.get('title', '不明な動画')
            
            # ファイル名に使用できない文字を置換
            safe_title = re.sub(r'[\\/*?:"<>|]', '_', video_title)  # Windowsの制限文字
            safe_title = re.sub(r'[\s]+', ' ', safe_title)  # 連続スペースを単一スペースに
            
            output_filename = f"{safe_title}_高画質.mp4"
            output_path = os.path.join(self.save_path, output_filename)
            
            # FFmpegを使用して動画と音声を結合
            self.progress_signal.emit(0, "動画と音声を結合中...")
            
            # FFmpegコマンドを直接実行
            import subprocess
            
            # FFmpegコマンド構築 - QuickTime互換性向上版
            ffmpeg_cmd = [
                'ffmpeg',
                '-i', video_filename,  # 動画入力
                '-i', audio_filename,  # 音声入力
                '-c:v', 'copy',        # 動画はそのままコピー
                '-c:a', 'aac',         # 音声はAACにエンコード
                '-strict', 'experimental',
                '-movflags', '+faststart',      # MP4のメタデータをファイル先頭に配置
                '-brand', 'mp42',              # MP4コンテナをAppleデバイスと互換性のあるブランドに設定
                '-pix_fmt', 'yuv420p',         # QuickTimeと互換性のある色空間を指定
                '-map_metadata', '-1',         # 不要なメタデータを削除
                '-f', 'mp4',                   # 出力形式を明示的に指定
                output_path                    # 出力ファイル
            ]
            
            # 進捗表示を更新
            self.progress_signal.emit(50, "FFmpegで結合処理中...")
            
            # FFmpeg実行とタイムアウト設定
            try:
                # 処理が長いのでタイムアウトは設定せず、プログレス表示を改善
                self.progress_signal.emit(55, "FFmpegで動画と音声を結合中...")
                
                # コマンドをファイル名表示付きで表示
                ffmpeg_cmd_with_timeout = ffmpeg_cmd + ['-y']  # -y: 上書き確認なし
                
                # FFmpegプロセスを開始
                process = subprocess.Popen(
                    ffmpeg_cmd_with_timeout,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True,
                    bufsize=1
                )
                
                # 進捗状況を表示しながら待機
                for i in range(6):  # 10秒ごとに6回 = 最大60秒
                    if process.poll() is not None:
                        break  # プロセスが終了していれば抜ける
                    self.progress_signal.emit(55 + i*5, f"FFmpegで結合処理中... {i*10}秒経過")
                    time.sleep(10)
                
                # まだ終わっていない場合、完了まで待機
                if process.poll() is None:
                    self.progress_signal.emit(85, "FFmpegで結合処理中... もう少しお待ちください")
                    process.wait()
                
                # 終了コードを取得
                return_code = process.returncode
                stderr_output = process.stderr.read() if process.stderr else ""
                
                # エラーチェック
                if return_code != 0:
                    # 最初の方法が失敗した場合、シンプルな方法を試みる
                    self.progress_signal.emit(60, "別の方法で結合を試みています...")
                    
                    # シンプルな結合コマンド - この方法はほとんどの場合動作する
                    simple_cmd = [
                        'ffmpeg', '-y',
                        '-i', video_filename,
                        '-i', audio_filename,
                        '-c', 'copy',    # すべてコピー
                        '-f', 'mp4',
                        output_path
                    ]
                    
                    simple_process = subprocess.Popen(
                        simple_cmd,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    
                    # 進捗を表示しながら待機
                    for i in range(3):
                        if simple_process.poll() is not None:
                            break
                        self.progress_signal.emit(65 + i*5, f"シンプルな方法で結合中... {i*10}秒経過")
                        time.sleep(10)
                    
                    # 完了まで待機
                    if simple_process.poll() is None:
                        self.progress_signal.emit(75, "もう少しお待ちください...")
                        simple_process.wait()
                    
                    # 終了コードを取得
                    simple_return_code = simple_process.returncode
                    
                    if simple_return_code != 0:
                        # それでも失敗した場合、最後の手段として再エンコード
                        self.progress_signal.emit(70, "互換性向上のため再エンコード中...")
                        
                        # 再エンコードコマンド - より互換性の高い設定で
                        reencoding_cmd = [
                            'ffmpeg', '-y',
                            '-i', video_filename,
                            '-i', audio_filename,
                            '-c:v', 'libx264',         # H.264にエンコード
                            '-preset', 'fast',         # エンコード速度優先
                            '-profile:v', 'baseline',  # 基本的なプロファイル
                            '-c:a', 'aac',
                            '-b:a', '128k',            # 音声ビットレート指定
                            '-ac', '2',                # ステレオ音声
                            '-f', 'mp4',
                            output_path
                        ]
                        
                        # 再エンコード実行（長時間かかる可能性があるので進捗表示を改善）
                        final_process = subprocess.Popen(
                            reencoding_cmd,
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE
                        )
                        
                        # 進捗を表示しながら待機
                        for i in range(12):  # より長いタイムアウト（最大2分）
                            if final_process.poll() is not None:
                                break
                            self.progress_signal.emit(75 + i*2, f"再エンコード中... {i*10}秒経過")
                            time.sleep(10)
                            
                        # 完了まで待機
                        if final_process.poll() is None:
                            self.progress_signal.emit(95, "再エンコード完了間近...")
                            final_process.wait()
                        
                        if final_process.returncode != 0:
                            raise Exception("すべての結合方法が失敗しました。ダウンロードしたファイル形式が特殊な可能性があります。")
                
                self.progress_signal.emit(90, "処理完了")
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                raise Exception(f"FFmpeg処理中にエラーが発生しました: {str(e)}\n{error_details}")
            
            # 一時ファイルを削除
            if os.path.exists(video_filename):
                os.remove(video_filename)
            if os.path.exists(audio_filename):
                os.remove(audio_filename)
            
            self.finished_signal.emit(output_filename)
            
        except Exception as e:
            # エラー発生時に一時ファイルがあれば削除
            for path in [temp_video_path, temp_audio_path]:
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except:
                        pass
            
            raise e


class YouTubeDownloaderApp(QMainWindow):
    """YouTubeダウンローダーのメインアプリケーション"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("YouTube ダウンローダー (yt-dlp版)")
        self.setMinimumSize(700, 500)
        self.formats = None
        
        self.init_ui()
        
    def init_ui(self):
        # メインレイアウト
        main_layout = QVBoxLayout()
        
        # URL入力グループ
        url_group = QGroupBox("YouTube URL")
        url_layout = QVBoxLayout()
        
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("YouTube URLを入力してください")
        
        fetch_button = QPushButton("情報取得")
        fetch_button.clicked.connect(self.fetch_video_info)
        
        url_layout.addWidget(self.url_input)
        url_layout.addWidget(fetch_button)
        url_group.setLayout(url_layout)
        
        # 動画情報グループ
        info_group = QGroupBox("動画情報")
        info_layout = QVBoxLayout()
        
        self.title_label = QLabel("タイトル: ")
        self.title_label.setWordWrap(True)
        self.channel_label = QLabel("チャンネル: ")
        self.duration_label = QLabel("長さ: ")
        
        info_layout.addWidget(self.title_label)
        info_layout.addWidget(self.channel_label)
        info_layout.addWidget(self.duration_label)
        info_group.setLayout(info_layout)
        
        # 形式選択グループ
        format_group = QGroupBox("形式選択")
        format_layout = QVBoxLayout()
        
        # 高画質ダウンロードモードの選択チェックボックス
        self.high_quality_checkbox = QCheckBox("高画質ダウンロード（動画と音声を別々にダウンロードして結合）")
        format_layout.addWidget(self.high_quality_checkbox)
        
        # 高画質モードを選択した場合の説明ラベル
        self.high_quality_info = QLabel(
            "最高画質・音質を別々にダウンロードし、FFmpegで結合します。\n"
            "通常よりも高画質でダウンロードできますが、処理に時間がかかります。"
        )
        self.high_quality_info.setStyleSheet("color: #666;")
        format_layout.addWidget(self.high_quality_info)
        
        # チェックボックスの状態が変化したときのイベント接続
        self.high_quality_checkbox.stateChanged.connect(self.toggle_format_selection)
        
        # 通常の形式選択コンボボックス
        self.format_combo = QComboBox()
        self.format_combo.setMinimumWidth(600)
        format_layout.addWidget(self.format_combo)
        
        format_group.setLayout(format_layout)
        
        # 保存先グループ
        save_group = QGroupBox("保存先")
        save_layout = QHBoxLayout()
        
        self.save_path = os.path.expanduser("~/Downloads")
        self.save_path_label = QLabel(self.save_path)
        self.save_path_label.setWordWrap(True)
        
        browse_button = QPushButton("参照")
        browse_button.clicked.connect(self.browse_save_path)
        
        save_layout.addWidget(self.save_path_label)
        save_layout.addWidget(browse_button)
        save_group.setLayout(save_layout)
        
        # ダウンロードボタングループ
        download_group = QHBoxLayout()
        
        download_button = QPushButton("ダウンロード")
        download_button.clicked.connect(self.download_video)
        download_button.setMinimumHeight(40)
        
        download_group.addWidget(download_button)
        
        # 進捗バー
        progress_group = QGroupBox("ダウンロード状況")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        
        self.status_label = QLabel("準備完了")
        self.status_label.setWordWrap(True)
        
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addWidget(self.status_label)
        progress_group.setLayout(progress_layout)
        
        # レイアウトに追加
        main_layout.addWidget(url_group)
        main_layout.addWidget(info_group)
        main_layout.addWidget(format_group)
        main_layout.addWidget(save_group)
        main_layout.addLayout(download_group)
        main_layout.addWidget(progress_group)
        
        # ウィジェットをセット
        central_widget = QWidget()
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
    
    def toggle_format_selection(self, state):
        """高画質モードの選択状態に応じてUIを切り替える"""
        if state == Qt.Checked:
            self.format_combo.setEnabled(False)
            self.format_combo.setStyleSheet("color: #999;")
        else:
            self.format_combo.setEnabled(True)
            self.format_combo.setStyleSheet("")
    
    def browse_save_path(self):
        folder_path = QFileDialog.getExistingDirectory(self, "保存先を選択")
        if folder_path:
            self.save_path = folder_path
            self.save_path_label.setText(self.save_path)
    
    def fetch_video_info(self):
        url = self.url_input.text()
        if not url:
            QMessageBox.warning(self, "警告", "URLを入力してください")
            return
        
        self.status_label.setText("動画情報を取得中...")
        self.progress_bar.setValue(0)
        
        # 情報取得スレッドを開始
        self.info_thread = VideoInfoThread(url)
        self.info_thread.info_signal.connect(self.update_video_info)
        self.info_thread.error_signal.connect(self.show_error)
        self.info_thread.start()
    
    def format_duration(self, seconds):
        """秒を時:分:秒形式に変換"""
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if hours:
            return f"{int(hours)}時間{int(minutes)}分{int(seconds)}秒"
        else:
            return f"{int(minutes)}分{int(seconds)}秒"
    
    def format_filesize(self, bytes_size):
        """バイトサイズを読みやすい形式に変換"""
        if bytes_size is None:
            return "不明"
        
        # MB単位に変換
        mb_size = bytes_size / (1024 * 1024)
        
        if mb_size < 1000:
            return f"{mb_size:.2f} MB"
        else:
            # GB単位に変換
            gb_size = mb_size / 1024
            return f"{gb_size:.2f} GB"
    
    def update_video_info(self, info):
        """動画情報を更新"""
        try:
            # 基本情報を表示
            self.video_info = info
            self.title_label.setText(f"タイトル: {info['title']}")
            self.channel_label.setText(f"チャンネル: {info.get('channel', info.get('uploader', '不明'))}")
            
            # 長さを表示
            duration = info.get('duration')
            if duration:
                self.duration_label.setText(f"長さ: {self.format_duration(duration)}")
            else:
                self.duration_label.setText("長さ: 不明")
            
            # 形式情報をクリア
            self.format_combo.clear()
            
            # 形式情報を格納
            self.formats = []
            
            # 映像+音声の形式をリストに追加
            for fmt in info.get('formats', []):
                if (fmt.get('vcodec', 'none') != 'none' and 
                    fmt.get('acodec', 'none') != 'none'):
                    
                    # 形式情報を取得
                    format_id = fmt.get('format_id', '')
                    format_note = fmt.get('format_note', '')
                    ext = fmt.get('ext', '')
                    resolution = fmt.get('resolution', '')
                    filesize = self.format_filesize(fmt.get('filesize'))
                    
                    # 表示用の文字列を作成
                    display_text = f"{resolution} - {format_note} ({ext}) {filesize}"
                    
                    # コンボボックスに追加
                    self.format_combo.addItem(display_text, format_id)
                    self.formats.append(fmt)
            
            # 音声のみの形式を追加
            for fmt in info.get('formats', []):
                if (fmt.get('vcodec', '') == 'none' and 
                    fmt.get('acodec', 'none') != 'none'):
                    
                    format_id = fmt.get('format_id', '')
                    format_note = fmt.get('format_note', '')
                    ext = fmt.get('ext', '')
                    filesize = self.format_filesize(fmt.get('filesize'))
                    
                    display_text = f"音声のみ - {format_note} ({ext}) {filesize}"
                    
                    self.format_combo.addItem(display_text, format_id)
                    self.formats.append(fmt)
            
            # 情報取得完了
            self.status_label.setText("動画情報を取得しました。形式を選択してください。")
            
        except Exception as e:
            QMessageBox.critical(self, "エラー", f"情報の処理に失敗しました: {str(e)}")
            self.status_label.setText("エラーが発生しました")
    
    def show_error(self, error_message):
        """エラーメッセージを表示"""
        QMessageBox.critical(self, "エラー", error_message)
        self.status_label.setText("エラーが発生しました")
    
    def download_video(self):
        """動画をダウンロード"""
        if not hasattr(self, 'video_info'):
            QMessageBox.warning(self, "警告", "まず動画情報を取得してください")
            return
        
        # 高画質モードが選択されているかチェック
        is_high_quality = self.high_quality_checkbox.isChecked()
        
        if not is_high_quality and self.format_combo.count() == 0:
            QMessageBox.warning(self, "警告", "ダウンロード可能な形式がありません")
            return
        
        # 選択された形式IDを取得（高画質モードの場合は使用しない）
        format_id = self.format_combo.currentData() if not is_high_quality else None
        
        # 進捗バーをリセット
        self.progress_bar.setValue(0)
        
        if is_high_quality:
            self.status_label.setText("高画質ダウンロード準備中...")
        else:
            self.status_label.setText("ダウンロード準備中...")
        
        # ダウンロードスレッドを開始
        self.download_thread = DownloadThread(
            self.url_input.text(), 
            format_id, 
            self.save_path,
            is_high_quality
        )
        self.download_thread.progress_signal.connect(self.update_progress)
        self.download_thread.finished_signal.connect(self.download_finished)
        self.download_thread.error_signal.connect(self.show_error)
        self.download_thread.start()
    
    def update_progress(self, percentage, status):
        """ダウンロード進捗を更新"""
        if percentage >= 0:
            self.progress_bar.setValue(int(percentage))
        self.status_label.setText(f"ダウンロード中... {status}")
    
    def download_finished(self, filename):
        """ダウンロード完了時の処理"""
        self.progress_bar.setValue(100)
        self.status_label.setText(f"ダウンロード完了: {filename}")
        QMessageBox.information(self, "完了", f"ダウンロード完了: {filename}")


def main():
    """アプリケーションのエントリーポイント"""
    # macOSでのIMKエラーメッセージを抑制
    import os
    os.environ['QT_MAC_WANTS_LAYER'] = '1'
    
    # macOSでの警告を抑制
    import warnings
    warnings.filterwarnings("ignore")
    
    app = QApplication(sys.argv)
    window = YouTubeDownloaderApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()