#!/usr/bin/env python3
"""Create a Markdown page bundle without requiring Hugo to be installed."""
import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo


def main():
    parser = argparse.ArgumentParser(description='新建博客草稿')
    parser.add_argument('slug', help='英文地址，例如 my-first-post')
    parser.add_argument('title', help='文章标题')
    args = parser.parse_args()
    if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', args.slug):
        parser.error('slug 只能包含小写英文字母、数字和中间的连字符。')
    folder = Path(__file__).resolve().parents[1] / 'content' / 'posts' / args.slug
    if folder.exists():
        parser.error(f'目录已存在，不会覆盖：{folder}')
    folder.mkdir(parents=True)
    path = folder / 'index.md'
    title = json.dumps(args.title, ensure_ascii=False)
    date = datetime.now(ZoneInfo('Asia/Shanghai')).isoformat(timespec='seconds')
    path.write_text(f'---\ntitle: {title}\ndate: {date}\ndraft: true\nslug: {args.slug}\ndescription: ""\ntags: []\n---\n\n从你想记录的问题开始。\n', encoding='utf-8')
    print(f'已创建：{path}\n预览草稿：hugo server -D\n发布时填好 description，并把 draft 改成 false。')


if __name__ == '__main__':
    main()
