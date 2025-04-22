import os
import sys
from setuptools import setup, find_packages

# アプリケーション情報の定義
APP_NAME = "YouTube Downloader"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Kenta Kuzuhara"
APP_AUTHOR_EMAIL = ""
APP_DESCRIPTION = "YouTubeの動画を簡単にダウンロードするためのアプリケーション"
APP_URL = ""
APP_REQUIRES = ["PyQt5>=5.15.0", "yt-dlp>=2023.12.30"]

# setup関数の呼び出し
setup(
    name=APP_NAME.replace(" ", "_").lower(),
    version=APP_VERSION,
    author=APP_AUTHOR,
    author_email=APP_AUTHOR_EMAIL,
    description=APP_DESCRIPTION,
    url=APP_URL,
    packages=find_packages(),
    py_modules=["youtube_downloader_gui"],
    install_requires=APP_REQUIRES,
    entry_points={
        "console_scripts": [
            "youtube-downloader=youtube_downloader_gui:main",
        ],
    },
    python_requires=">=3.6",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Multimedia :: Video",
    ],
)