#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import markdown
import codecs
from datetime import datetime
import shutil
import re

MARKDOWN_DIR = "diary"  # Markdownファイルが置かれるディレクトリ
OUTPUT_DIR = "./docs"     # 出力先ディレクトリ（GitHub Pagesで使用）

# ディレクトリが存在しない場合は作成
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Markdownファイルを変換
def convert_markdown_files():
    # 出力ディレクトリの作成
    ensure_dir(OUTPUT_DIR)
    
    # スタイルファイルの作成
    create_css_file()
    
    # すべてのMarkdownファイルを取得
    md_files = glob.glob(os.path.join(MARKDOWN_DIR, "*.md"))
    print("=" * 10)
    print(md_files)
    print(glob.glob("./*"))
    print(glob.glob("./*/*"))
    entries = []
    
    for md_file in md_files:
        # ファイル名から情報を取得
        basename = os.path.basename(md_file)
        filename_without_ext = os.path.splitext(basename)[0]
        
        # 日付の抽出（diary-YYYY-MM-DD 形式を想定）
        # 日付の抽出を単純化（より確実に動作するように）
        if filename_without_ext.startswith('diary-'):
            date_str = filename_without_ext[6:]  # 'diary-' の後の部分を抽出
        else:
            date_str = ''
        
        print(f"処理中: {basename}, 抽出された日付: {date_str}")
        
        html_filename = filename_without_ext + ".html"
        output_path = os.path.join(OUTPUT_DIR, html_filename)
        
        # Markdownの内容を読み込み
        with codecs.open(md_file, "r", encoding="utf-8") as f:
            md_content = f.read()
        
        # タイトルを取得（最初の行が # で始まる場合）
        title = filename_without_ext
        lines = md_content.split('\n')
        if lines and lines[0].startswith('# '):
            title = lines[0][2:].strip()
        
        # Markdownを変換
        html_content = markdown.markdown(md_content, extensions=['extra'])
        
        # HTMLテンプレートに挿入
        html = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1 class="site-title"><a href="index.html">私の日記</a></h1>
            <nav>
                <a href="index.html">ホーム</a>
                <a href="archives.html">アーカイブ</a>
            </nav>
        </header>
        
        <main>
            {content}
        </main>

        <footer>
            <p>&copy; {year} My Diary</p>
            <p>最終更新: {last_updated}</p>
        </footer>
    </div>
</body>
</html>""".format(
            title=title,
            content=html_content,
            year=datetime.now().strftime('%Y'),
            last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # HTMLファイルを保存
        with codecs.open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        
        # エントリ情報を保存（インデックス用）
        entries.append({
            'title': title,
            'file': html_filename,
            'date': date_str
        })
    
    return entries

# インデックスページの作成
def create_index_page(entries):
    # エントリを日付で降順ソート
    entries.sort(key=lambda x: x['date'], reverse=True)
    
    # インデックスのHTML内容を作成
    content = "<h1>日記一覧</h1>\n<ul class=\"post-list\">\n"
    
    for entry in entries:
        date_display = entry['date'] if entry['date'] else '日付なし'
        content += f'<li class="post-item">\n'
        content += f'  <span class="post-date">{date_display}</span>\n'
        content += f'  <a href="{entry["file"]}" class="post-link">{entry["title"]}</a>\n'
        content += f'</li>\n'
    
    content += "</ul>"
    
    # HTMLテンプレートに挿入
    html = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>私の日記</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1 class="site-title"><a href="index.html">私の日記</a></h1>
            <nav>
                <a href="index.html">ホーム</a>
                <a href="archives.html">アーカイブ</a>
            </nav>
        </header>
        
        <main>
            {content}
        </main>

        <footer>
            <p>&copy; {year} My Diary</p>
            <p>最終更新: {last_updated}</p>
        </footer>
    </div>
</body>
</html>""".format(
        content=content,
        year=datetime.now().strftime('%Y'),
        last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    
    # HTMLファイルを保存
    with codecs.open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

# アーカイブページの作成
def create_archives_page(entries):
    # 年月ごとにエントリをグループ化
    archives = {}
    
    for entry in entries:
        if entry['date']:
            parts = entry['date'].split('-')
            if len(parts) >= 2:
                year_month = f"{parts[0]}-{parts[1]}"
                if year_month not in archives:
                    archives[year_month] = []
                archives[year_month].append(entry)
    
    # アーカイブのHTML内容を作成
    content = "<h1>アーカイブ</h1>\n"
    
    for year_month, month_entries in sorted(archives.items(), reverse=True):
        content += f"<h2 class=\"archive-date\">{year_month}</h2>\n<ul class=\"archive-list\">\n"
        for entry in month_entries:
            content += f'<li class="archive-item"><a href="{entry["file"]}">{entry["title"]}</a></li>\n'
        content += "</ul>\n"
    
    # HTMLテンプレートに挿入
    html = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>アーカイブ - 私の日記</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1 class="site-title"><a href="index.html">私の日記</a></h1>
            <nav>
                <a href="index.html">ホーム</a>
                <a href="archives.html">アーカイブ</a>
            </nav>
        </header>
        
        <main>
            {content}
        </main>

        <footer>
            <p>&copy; {year} My Diary</p>
            <p>最終更新: {last_updated}</p>
        </footer>
    </div>
</body>
</html>""".format(
        content=content,
        year=datetime.now().strftime('%Y'),
        last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    
    # HTMLファイルを保存
    with codecs.open(os.path.join(OUTPUT_DIR, "archives.html"), "w", encoding="utf-8") as f:
        f.write(html)

# CSSファイルの作成
def create_css_file():
    css_content = """/* シンプルなスタイル */
body {
    font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
    line-height: 1.7;
    color: #333;
    background-color: #fff;
    margin: 0;
    padding: 0;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

header {
    margin-bottom: 30px;
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
}

.site-title {
    margin: 0;
    padding: 0;
}

.site-title a {
    text-decoration: none;
    color: #333;
}

.site-title a:hover {
    color: #4a89dc;
}

nav {
    margin-top: 10px;
}

nav a {
    margin-right: 15px;
    text-decoration: none;
    color: #0066cc;
}

nav a:hover {
    text-decoration: underline;
}

main {
    margin-bottom: 50px;
}

footer {
    border-top: 1px solid #eee;
    padding-top: 10px;
    font-size: 0.8em;
    color: #666;
}

h1, h2, h3, h4, h5, h6 {
    color: #222;
}

a {
    color: #0066cc;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

ul {
    padding-left: 20px;
}

img {
    max-width: 100%;
    height: auto;
    border: 1px solid #eee;
    border-radius: 4px;
}

/* 記事一覧のスタイル */
.post-list {
    list-style: none;
    padding: 0;
}

.post-item {
    margin-bottom: 20px;
    padding-bottom: 10px;
    border-bottom: 1px solid #eee;
}

.post-date {
    display: block;
    color: #666;
    font-size: 0.9em;
}

.post-link {
    font-size: 1.2em;
    font-weight: bold;
}

/* アーカイブページのスタイル */
.archive-date {
    margin-top: 30px;
    padding-bottom: 5px;
    border-bottom: 1px solid #eee;
}

.archive-list {
    list-style: none;
    padding-left: 10px;
}

.archive-item {
    margin-bottom: 8px;
}

/* コードブロックのスタイル */
pre, code {
    font-family: monospace;
    background-color: #f6f8fa;
    border-radius: 3px;
}

pre {
    padding: 16px;
    overflow: auto;
    font-size: 85%;
    line-height: 1.45;
    border: 1px solid #ddd;
}

code {
    padding: 0.2em 0.4em;
    margin: 0;
    font-size: 85%;
}

/* レスポンシブデザイン */
@media (max-width: 600px) {
    .container {
        padding: 10px;
    }
    
    .site-title {
        font-size: 1.5em;
    }
    
    nav a {
        margin-right: 10px;
        font-size: 0.9em;
    }
}
"""
    
    # CSSファイルを保存
    with codecs.open(os.path.join(OUTPUT_DIR, "style.css"), "w", encoding="utf-8") as f:
        f.write(css_content)

# 404ページの作成
def create_404_page():
    html = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>404 - ページが見つかりません</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1 class="site-title"><a href="index.html">私の日記</a></h1>
            <nav>
                <a href="index.html">ホーム</a>
                <a href="archives.html">アーカイブ</a>
            </nav>
        </header>
        
        <main>
            <div class="error-page">
                <h1>404</h1>
                <h2>ページが見つかりません</h2>
                <p>お探しのページは移動または削除された可能性があります。</p>
                <p><a href="index.html">トップページに戻る</a></p>
            </div>
        </main>

        <footer>
            <p>&copy; {year} My Diary</p>
            <p>最終更新: {last_updated}</p>
        </footer>
    </div>
</body>
</html>""".format(
        year=datetime.now().strftime('%Y'),
        last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    
    with codecs.open(os.path.join(OUTPUT_DIR, "404.html"), "w", encoding="utf-8") as f:
        f.write(html)

# メイン処理
def main():
    print("Markdown ファイルを HTML に変換しています...")
    
    # Markdownディレクトリが存在しない場合は作成
    ensure_dir(MARKDOWN_DIR)

    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)

    # ファイルの変換
    entries = convert_markdown_files()
    
    # インデックスページの作成
    create_index_page(entries)
    
    # アーカイブページの作成
    create_archives_page(entries)
    
    # 404ページの作成
    create_404_page()
    
    print(f"変換完了: {len(entries)} ファイルを {OUTPUT_DIR} ディレクトリに出力しました。")

if __name__ == "__main__":
    main()
