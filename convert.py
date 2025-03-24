#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import glob
import markdown
import codecs
from datetime import datetime
import shutil
import re
from mdx_linkify.mdx_linkify import LinkifyExtension
from markdown.extensions.toc import TocExtension
from markdown.extensions.codehilite import CodeHiliteExtension
from mdx_math import MathExtension

# 設定
MARKDOWN_DIR = "diary"  # Markdownファイルが置かれるディレクトリ
OUTPUT_DIR = "docs"     # 出力先ディレクトリ（GitHub Pagesで使用）
TEMPLATE_PATH = "template.html"  # HTMLテンプレートファイル

# ディレクトリが存在しない場合は作成
def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Markdownに追加の拡張機能を適用する
def convert_markdown_to_html(md_content):
    # 拡張機能のリスト
    extensions = [
        'extra',  # テーブルなどの追加機能
        'meta',   # メタデータ
        LinkifyExtension(),  # URLを自動的にリンクに変換
        TocExtension(permalink=True),  # 目次
        CodeHiliteExtension(linenums=True),  # コードハイライト
        MathExtension(enable_dollar_delimiter=True)  # 数式
    ]
    
    # Markdownを変換
    return markdown.markdown(md_content, extensions=extensions)

# Markdownファイルを変換
def convert_markdown_files():
    # 出力ディレクトリの作成
    ensure_dir(OUTPUT_DIR)
    
    # 画像ディレクトリの作成
    images_dir = os.path.join(OUTPUT_DIR, "images")
    ensure_dir(images_dir)
    
    # すべてのMarkdownファイルを取得
    md_files = glob.glob(os.path.join(MARKDOWN_DIR, "*.md"))
    entries = []
    
    for md_file in md_files:
        # ファイル名から情報を取得
        basename = os.path.basename(md_file)
        filename_without_ext = os.path.splitext(basename)[0]
        
        # 日付の抽出（diary-YYYY-MM-DD 形式を想定）
        date_match = re.match(r'diary-(\d{4}-\d{2}-\d{2})', filename_without_ext)
        date_str = date_match.group(1) if date_match else ''
        
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
        
        # メタデータの作成
        meta = {
            'title': title,
            'date': date_str,
            'layout': 'default'
        }
        
        # FrontMatterの作成
        front_matter = "---\n"
        for key, value in meta.items():
            front_matter += f"{key}: {value}\n"
        front_matter += "---\n\n"
        
        # 画像の処理 (markdown内の画像を処理する場合)
        # ![alt](image.jpg) 形式の画像を見つけて、imagesディレクトリにコピー
        img_pattern = r'!\[(.*?)\]\((.*?)\)'
        for match in re.finditer(img_pattern, md_content):
            img_path = match.group(2)
            if not img_path.startswith('http'):  # ローカル画像のみ処理
                img_basename = os.path.basename(img_path)
                img_src_path = os.path.join(os.path.dirname(md_file), img_path)
                img_dest_path = os.path.join(images_dir, img_basename)
                
                if os.path.exists(img_src_path):
                    shutil.copy2(img_src_path, img_dest_path)
                    # 画像パスの更新
                    md_content = md_content.replace(
                        f'({img_path})', 
                        f'(/images/{img_basename})'
                    )
        
        # Markdownを変換
        html_content = convert_markdown_to_html(md_content)
        
        # FrontMatterとHTMLを合わせて保存
        with codecs.open(output_path, "w", encoding="utf-8") as f:
            f.write(front_matter + html_content)
        
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
    
    # FrontMatterの作成
    front_matter = """---
layout: default
title: 私の日記
---

"""
    
    # HTMLファイルを保存
    with codecs.open(os.path.join(OUTPUT_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(front_matter + content)

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
    
    # FrontMatterの作成
    front_matter = """---
layout: default
title: アーカイブ
---

"""
    
    # HTMLファイルを保存
    with codecs.open(os.path.join(OUTPUT_DIR, "archives.html"), "w", encoding="utf-8") as f:
        f.write(front_matter + content)

# タグページの作成（タグがある場合）
def create_tags_page(entries):
    # タグごとにエントリをグループ化
    tags = {}
    
    for entry in entries:
        # タグの抽出（Markdown内で #tag 形式でタグが付けられていると仮定）
        md_file = os.path.join(MARKDOWN_DIR, entry['file'].replace('.html', '.md'))
        if os.path.exists(md_file):
            with codecs.open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # タグの検索（簡易的な実装）
                tag_matches = re.findall(r'#(\w+)', content)
                for tag in tag_matches:
                    if tag not in tags:
                        tags[tag] = []
                    tags[tag].append(entry)
    
    # タグがない場合は処理しない
    if not tags:
        return
    
    # タグページのHTML内容を作成
    content = "<h1>タグ一覧</h1>\n"
    
    for tag, tag_entries in sorted(tags.items()):
        content += f"<h2 class=\"tag-name\">#{tag}</h2>\n<ul class=\"tag-list\">\n"
        for entry in tag_entries:
            content += f'<li class="tag-item"><a href="{entry["file"]}">{entry["title"]}</a></li>\n'
        content += "</ul>\n"
    
    # FrontMatterの作成
    front_matter = """---
layout: default
title: タグ
---

"""
    
    # HTMLファイルを保存
    with codecs.open(os.path.join(OUTPUT_DIR, "tags.html"), "w", encoding="utf-8") as f:
        f.write(front_matter + content)

# Jekyll用のディレクトリ構造を作成
def create_jekyll_structure():
    # _layouts ディレクトリの作成
    layouts_dir = os.path.join(OUTPUT_DIR, "_layouts")
    ensure_dir(layouts_dir)
    
    # assets/css ディレクトリの作成
    assets_css_dir = os.path.join(OUTPUT_DIR, "assets", "css")
    ensure_dir(assets_css_dir)

    # _includes ディレクトリの作成
    includes_dir = os.path.join(OUTPUT_DIR, "_includes")
    ensure_dir(includes_dir)
    
    # デフォルトレイアウトの作成
    default_layout = """<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page.title }}</title>
    <link rel="stylesheet" href="{{ '/assets/css/style.css' | relative_url }}">
    {% if page.use_math %}
    <script type="text/javascript" async
      src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
    </script>
    {% endif %}
</head>
<body>
    <div class="container">
        <header class="site-header">
            <h1 class="site-title"><a href="{{ '/' | relative_url }}">私の日記</a></h1>
            <nav class="site-nav">
                <a href="{{ '/' | relative_url }}">ホーム</a>
                <a href="{{ '/archives.html' | relative_url }}">アーカイブ</a>
                {% if site.tags_enabled %}<a href="{{ '/tags.html' | relative_url }}">タグ</a>{% endif %}
            </nav>
        </header>

        <main class="site-content">
            {{ content }}
        </main>

        <footer class="site-footer">
            <p>&copy; {{ site.time | date: '%Y' }} My Diary</p>
            <p>最終更新: {{ site.time | date: '%Y-%m-%d %H:%M:%S' }}</p>
        </footer>
    </div>
</body>
</html>"""
    
    with codecs.open(os.path.join(layouts_dir, "default.html"), "w", encoding="utf-8") as f:
        f.write(default_layout)
    
    # ヘッダーのインクルードファイル作成
    header_include = """<header class="site-header">
    <h1 class="site-title"><a href="{{ '/' | relative_url }}">私の日記</a></h1>
    <nav class="site-nav">
        <a href="{{ '/' | relative_url }}">ホーム</a>
        <a href="{{ '/archives.html' | relative_url }}">アーカイブ</a>
        {% if site.tags_enabled %}<a href="{{ '/tags.html' | relative_url }}">タグ</a>{% endif %}
    </nav>
</header>"""
    
    with codecs.open(os.path.join(includes_dir, "header.html"), "w", encoding="utf-8") as f:
        f.write(header_include)
    
    # フッターのインクルードファイル作成
    footer_include = """<footer class="site-footer">
    <p>&copy; {{ site.time | date: '%Y' }} My Diary</p>
    <p>最終更新: {{ site.time | date: '%Y-%m-%d %H:%M:%S' }}</p>
</footer>"""
    
    with codecs.open(os.path.join(includes_dir, "footer.html"), "w", encoding="utf-8") as f:
        f.write(footer_include)
    
    # style.scss ファイルの作成
    scss_content = """---
---

@import "{{ site.theme }}";

// カスタムスタイル
:root {
  --main-bg-color: #fff;
  --main-text-color: #333;
  --header-bg-color: #f5f5f5;
  --link-color: #0066cc;
  --border-color: #eee;
  --accent-color: #4a89dc;
}

body {
    font-family: 'Helvetica Neue', Arial, 'Hiragino Kaku Gothic ProN', 'Hiragino Sans', Meiryo, sans-serif;
    line-height: 1.7;
    color: var(--main-text-color);
    background-color: var(--main-bg-color);
    margin: 0;
    padding: 0;
}

.container {
    max-width: 800px;
    margin: 0 auto;
    padding: 20px;
}

.site-header {
    margin-bottom: 30px;
    border-bottom: 1px solid var(--border-color);
    padding-bottom: 10px;
}

.site-title {
    margin: 0;
    padding: 0;
    
    a {
        text-decoration: none;
        color: var(--main-text-color);
        
        &:hover {
            color: var(--accent-color);
        }
    }
}

.site-nav {
    margin-top: 10px;
    
    a {
        margin-right: 15px;
        text-decoration: none;
        color: var(--link-color);
        
        &:hover {
            text-decoration: underline;
        }
    }
}

.site-content {
    margin-bottom: 50px;
}

.site-footer {
    border-top: 1px solid var(--border-color);
    padding-top: 10px;
    font-size: 0.8em;
    color: #666;
}

h1, h2, h3, h4, h5, h6 {
    color: #222;
}

a {
    color: var(--link-color);
    text-decoration: none;
    
    &:hover {
        text-decoration: underline;
    }
}

ul {
    padding-left: 20px;
}

img {
    max-width: 100%;
    height: auto;
    border: 1px solid var(--border-color);
    border-radius: 4px;
}

// 記事一覧のスタイル
.post-list {
    list-style: none;
    padding: 0;
    
    .post-item {
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 1px solid var(--border-color);
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
}

// アーカイブページのスタイル
.archive-date {
    margin-top: 30px;
    padding-bottom: 5px;
    border-bottom: 1px solid var(--border-color);
}

.archive-list {
    list-style: none;
    padding-left: 10px;
}

.archive-item {
    margin-bottom: 8px;
}

// タグページのスタイル
.tag-name {
    margin-top: 30px;
    color: var(--accent-color);
}

.tag-list {
    list-style: none;
    padding-left: 10px;
}

.tag-item {
    margin-bottom: 8px;
}

// コードブロックのスタイル
pre, code {
    font-family: 'Courier New', Courier, monospace;
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

// 数式のスタイル
.math {
    overflow-x: auto;
}

// レスポンシブデザイン
@media (max-width: 600px) {
    .container {
        padding: 10px;
    }
    
    .site-title {
        font-size: 1.5em;
    }
    
    .site-nav {
        a {
            margin-right: 10px;
            font-size: 0.9em;
        }
    }
}
"""
    
    with codecs.open(os.path.join(assets_css_dir, "style.scss"), "w", encoding="utf-8") as f:
        f.write(scss_content)

# _config.yml ファイルの作成
def create_config_file():
    config_content = """# Site settings
title: 私の日記
description: Markdownで書かれた日記をGitHub Pagesで公開
baseurl: ""
url: ""

# Build settings
markdown: kramdown
highlighter: rouge
kramdown:
  input: GFM
  syntax_highlighter: rouge

# カスタム設定
tags_enabled: true

# プラグイン（GitHub Pagesで利用可能なもの）
plugins:
  - jekyll-feed
  - jekyll-seo-tag

# 除外するファイル/ディレクトリ
exclude:
  - Gemfile
  - Gemfile.lock
  - node_modules
  - vendor
  - .github
  - README.md
  - convert.py
  - diary

# Sass設定
sass:
  style: compressed

# デフォルトの設定
defaults:
  -
    scope:
      path: "" # すべてのファイル
    values:
      layout: "default"
"""
    
    # ルートと出力ディレクトリの両方に _config.yml を配置
    with codecs.open("_config.yml", "w", encoding="utf-8") as f:
        f.write(config_content)
    
    with codecs.open(os.path.join(OUTPUT_DIR, "_config.yml"), "w", encoding="utf-8") as f:
        f.write(config_content)

# 404ページの作成
def create_404_page():
    content = """---
layout: default
title: 404 - ページが見つかりません
permalink: /404.html
---

<div class="error-page">
  <h1>404</h1>
  <h2>ページが見つかりません</h2>
  <p>お探しのページは移動または削除された可能性があります。</p>
  <p><a href="{{ '/' | relative_url }}">トップページに戻る</a></p>
</div>
"""
    
    with codecs.open(os.path.join(OUTPUT_DIR, "404.html"), "w", encoding="utf-8") as f:
        f.write(content)

# メイン処理
def main():
    print("Markdown ファイルを HTML に変換しています...")
    
    # Markdownディレクトリが存在しない場合は作成
    ensure_dir(MARKDOWN_DIR)
    
    # 出力ディレクトリが存在する場合はクリーンアップ
    if os.path.exists(OUTPUT_DIR):
        for item in os.listdir(OUTPUT_DIR):
            item_path = os.path.join(OUTPUT_DIR, item)
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)
            else:
                os.remove(item_path)
    
    # GitHub Pages 用の Jekyll 構造を作成
    create_jekyll_structure()
    
    # 設定ファイルの作成
    create_config_file()
    
    # 404ページの作成
    create_404_page()
    
    # ファイルの変換
    entries = convert_markdown_files()
    
    # インデックスページの作成
    create_index_page(entries)
    
    # アーカイブページの作成
    create_archives_page(entries)
    
    # タグページの作成（任意）
    create_tags_page(entries)
    
    print(f"変換完了: {len(entries)} ファイルを {OUTPUT_DIR} ディレクトリに出力しました。")

if __name__ == "__main__":
    main()
