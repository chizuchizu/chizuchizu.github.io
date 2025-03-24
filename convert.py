#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import markdown
import codecs
from datetime import datetime

# 設定
MARKDOWN_DIR = "diary"  # Markdownファイルが置かれるディレクトリ
OUTPUT_DIR = "docs"     # 出力先ディレクトリ（GitHub Pagesで使用）
TEMPLATE_PATH = "template.html"  # HTMLテンプレートファイル

# テンプレートの内容
TEMPLATE = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{title}}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <header>
        <h1>私の日記</h1>
        <nav>
            <a href="index.html">ホーム</a>
            <a href="archives.html">アーカイブ</a>
        </nav>
    </header>
    
    <main>
        {{content}}
    </main>

    <footer>
        <p>&copy; 2025 My Diary</p>
        <p>最終更新: {{last_updated}}</p>
    </footer>
</body>
</html>
"""

# ディレクトリが存在しない場合は作成
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Markdownファイルを変換
def convert_markdown_files():
    # 出力ディレクトリの作成
    ensure_dir(OUTPUT_DIR)
    
    # テンプレートファイルの作成
    with codecs.open(TEMPLATE_PATH, "w", encoding="utf-8") as f:
        f.write(TEMPLATE)
    
    # すべてのMarkdownファイルを取得
    md_files = glob.glob(os.path.join(MARKDOWN_DIR, "*.md"))
    entries = []
    
    for md_file in md_files:
        # ファイル名から情報を取得
        basename = os.path.basename(md_file)
        filename_without_ext = os.path.splitext(basename)[0]
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
        
        # テンプレートに挿入
        last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        html = TEMPLATE.replace('{{title}}', title)
        html = html.replace('{{content}}', html_content)
        html = html.replace('{{last_updated}}', last_updated)
        
        # HTMLファイルを保存
        with codecs.open(output_path, "w", encoding="utf-8") as f:
            f.write(html)
        
        # エントリ情報を保存（インデックス用）
        entries.append({
            'title': title,
            'file': html_filename,
            'date': filename_without_ext if filename_without_ext.startswith('diary-') else ''
        })
    
    return entries

# インデックスページの作成
def create_index_page(entries):
    # エントリを日付で降順ソート
    entries.sort(key=lambda x: x['date'], reverse=True)
    
    # インデックスのHTML内容を作成
    content = "<h1>日記一覧</h1>\n<ul>\n"
    
    for entry in entries:
        content += f'<li><a href="{entry["file"]}">{entry["title"]}</a></li>\n'
    
    content += "</ul>"
    
    # テンプレートに挿入
    last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    html = TEMPLATE.replace('{{title}}', '私の日記')
    html = html.replace('{{content}}', content)
    html = html.replace('{{last_updated}}', last_updated)
    
    # HTMLファイルを保存
    with codecs.open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(html)

# アーカイブページの作成
def create_archives_page(entries):
    # 年月ごとにエントリをグループ化
    archives = {}
    
    for entry in entries:
        if entry['date'].startswith('diary-'):
            try:
                # diary-YYYY-MM-DD 形式から年月を抽出
                parts = entry['date'].split('-')
                if len(parts) >= 3:
                    year_month = f"{parts[1]}-{parts[2]}"
                    if year_month not in archives:
                        archives[year_month] = []
                    archives[year_month].append(entry)
            except:
                pass
    
    # アーカイブのHTML内容を作成
    content = "<h1>アーカイブ</h1>\n"
    
    for year_month, month_entries in sorted(archives.items(), reverse=True):
        content += f"<h2>{year_month}</h2>\n<ul>\n"
        for entry in month_entries:
            content += f'<li><a href="{entry["file"]}">{entry["title"]}</a></li>\n'
        content += "</ul>\n"
    
    # テンプレートに挿入
    last_updated = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    html = TEMPLATE.replace('{{title}}', 'アーカイブ - 私の日記')
    html = html.replace('{{content}}', content)
    html = html.replace('{{last_updated}}', last_updated)
    
    # HTMLファイルを保存
    with codecs.open(os.path.join(OUTPUT_DIR, "archives.html"), "w", encoding="utf-8") as f:
        f.write(html)

# CSSの作成
def create_css():
    css_content = """
body {
    font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
    line-height: 1.7;
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
    color: #333;
}

header {
    margin-bottom: 30px;
    border-bottom: 1px solid #eee;
    padding-bottom: 10px;
}

header h1 {
    margin: 0;
    padding: 0;
}

nav {
    margin-top: 10px;
}

nav a {
    margin-right: 15px;
    text-decoration: none;
    color: #0066cc;
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
}
"""
    # CSSファイルを保存
    with codecs.open(os.path.join(OUTPUT_DIR, "style.css"), "w", encoding="utf-8") as f:
        f.write(css_content)

# メイン処理
def main():
    print("Markdown ファイルを HTML に変換しています...")
    
    # Markdownディレクトリが存在しない場合は作成
    ensure_dir(MARKDOWN_DIR)
    
    # ファイルの変換
    entries = convert_markdown_files()
    
    # インデックスページの作成
    create_index_page(entries)
    
    # アーカイブページの作成
    create_archives_page(entries)
    
    # CSSの作成
    create_css()
    
    print(f"変換完了: {len(entries)} ファイルを {OUTPUT_DIR} ディレクトリに出力しました。")

if __name__ == "__main__":
    main()
