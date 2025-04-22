#!/usr/bin/env python3
"""
YouTubeダウンローダー - インストールスクリプト
必要な依存関係をインストールし、アプリケーションを設定します。
"""

import os
import sys
import subprocess
import platform

def check_python_version():
    """Pythonのバージョンをチェック"""
    if sys.version_info < (3, 6):
        print("エラー: Python 3.6以上が必要です")
        sys.exit(1)
    print(f"Python {sys.version.split()[0]} を検出しました ✓")

def install_pip_packages():
    """必要なPipパッケージをインストール"""
    print("PyQt5とyt-dlpをインストールしています...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "PyQt5>=5.15.0", "yt-dlp>=2023.12.30"])
        print("パッケージのインストールが完了しました ✓")
    except subprocess.CalledProcessError:
        print("エラー: パッケージのインストールに失敗しました")
        sys.exit(1)

def check_ffmpeg():
    """FFmpegがインストールされているか確認"""
    try:
        subprocess.check_output(["ffmpeg", "-version"])
        print("FFmpegが見つかりました ✓")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("FFmpegが見つかりませんでした ✗")
        return False

def install_ffmpeg():
    """システムに応じたFFmpegのインストール方法を表示"""
    system = platform.system()
    
    print("\nFFmpegのインストール方法:")
    
    if system == "Windows":
        print("""
Windows:
1. https://ffmpeg.org/download.html からFFmpegをダウンロード
2. zipファイルを解凍し、中身をC:\\ffmpegなどに配置
3. 環境変数のPathにC:\\ffmpeg\\binを追加
        """)
    elif system == "Darwin":  # macOS
        print("""
macOS:
1. Homebrewがインストールされていない場合は、以下のコマンドでインストール:
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
2. 以下のコマンドでFFmpegをインストール:
   brew install ffmpeg
        """)
    elif system == "Linux":
        print("""
Linux (Ubuntu/Debian):
   sudo apt update
   sudo apt install ffmpeg

Linux (Fedora):
   sudo dnf install ffmpeg

Linux (Arch):
   sudo pacman -S ffmpeg
        """)
    
    print("FFmpegをインストールした後、このスクリプトを再実行してください。")

def create_shortcut():
    """デスクトップにショートカットを作成"""
    system = platform.system()
    
    if system == "Windows":
        # Windowsの場合、PythonのScriptsディレクトリにexeファイルが作成される
        try:
            import winshell
            from win32com.client import Dispatch
            
            desktop = winshell.desktop()
            path = os.path.join(desktop, "YouTube Downloader.lnk")
            
            target = os.path.join(sys.exec_prefix, "Scripts", "youtube-downloader.exe")
            
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = target
            shortcut.WorkingDirectory = desktop
            shortcut.IconLocation = target
            shortcut.save()
            
            print("デスクトップにショートカットを作成しました ✓")
        except ImportError:
            print("ショートカット作成に必要なライブラリがありません")
            print("Windowsの場合、以下のコマンドでアプリを起動できます: youtube-downloader")
    else:
        # macOSとLinuxの場合
        print(f"インストールが完了しました。'youtube-downloader'コマンドで起動できます。")

def main():
    """メイン関数"""
    print("YouTube Downloader インストーラー")
    print("=" * 30)
    
    # Pythonバージョンのチェック
    check_python_version()
    
    # 必要なパッケージをインストール
    install_pip_packages()
    
    # FFmpegのチェック
    if not check_ffmpeg():
        install_ffmpeg()
        print("\n注意: FFmpegがインストールされていないため、高画質ダウンロード機能は使用できません。")
        print("基本的なダウンロード機能は使用可能です。")
    
    # 現在のスクリプトをパッケージとしてインストール
    print("\nYouTube Downloaderアプリケーションをインストールしています...")
    try:
        # カレントディレクトリをスクリプトの場所に変更
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        # pipを使ってインストール
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", "."])
        print("アプリケーションのインストールが完了しました ✓")
        
        # ショートカットの作成
        create_shortcut()
        
    except subprocess.CalledProcessError:
        print("エラー: アプリケーションのインストールに失敗しました")
        sys.exit(1)
    
    print("\nインストールが完了しました！")
    print("'youtube-downloader'コマンドを実行して、アプリケーションを起動できます。")

if __name__ == "__main__":
    main()