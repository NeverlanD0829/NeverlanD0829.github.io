#!/usr/bin/env python3
"""Check output links, anchors, search data and feeds using the standard library."""
import argparse
import json
import sys
import tomllib
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urljoin, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.duplicate_ids = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if 'id' in attrs:
            if attrs['id'] in self.ids:
                self.duplicate_ids.append(attrs['id'])
            self.ids.add(attrs['id'])
        for attr in ['href', 'src']:
            if attrs.get(attr):
                self.links.append(attrs[attr])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--directory', type=Path, default=ROOT / 'public')
    parser.add_argument('--base-url', default=None)
    args = parser.parse_args()
    output = args.directory.resolve()
    config = tomllib.loads((ROOT / 'hugo.toml').read_text(encoding='utf-8'))
    base = args.base_url or config['baseURL']
    base_parts = urlsplit(base)
    base_path = base_parts.path.rstrip('/') + '/'
    errors = []
    files = list(output.rglob('*.html'))
    pages = {path: Page(path.read_text(encoding='utf-8')) for path in files}
    if not files:
        errors.append('没有生成 HTML。请先运行 hugo。')

    def resolve(url, origin):
        parts = urlsplit(urljoin(origin, url))
        if parts.scheme not in ('http', 'https') or parts.netloc != base_parts.netloc:
            return None, ''
        decoded = unquote(parts.path)
        if not decoded.startswith(unquote(base_path)):
            errors.append(f'链接超出站点路径：{url}')
            return None, ''
        target = (output / decoded[len(unquote(base_path)):]).resolve()
        if not target.is_relative_to(output):
            errors.append(f'链接超出输出目录：{url}')
            return None, ''
        if target.is_dir():
            target = target / 'index.html'
        return target, unquote(parts.fragment)

    for path, page in pages.items():
        relative = path.relative_to(output).as_posix()
        page_url = urljoin(base, relative.removesuffix('index.html'))
        for duplicate in page.duplicate_ids:
            errors.append(f'{relative}: 重复 id {duplicate}')
        for url in page.links:
            target, fragment = resolve(url, page_url)
            if target is None:
                continue
            if not target.is_file():
                errors.append(f'{relative}: 链接目标不存在 {url}')
            elif fragment and target in pages and fragment not in pages[target].ids:
                errors.append(f'{relative}: 锚点不存在 {url}')

    try:
        search = json.loads((output / 'index.json').read_text(encoding='utf-8'))
        if not isinstance(search, list):
            raise ValueError('搜索索引应为数组')
        for post in search:
            if not post.get('title') or not post.get('content'):
                errors.append('搜索条目缺少标题或正文')
            target, _ = resolve(post['url'], base)
            if target not in pages:
                errors.append(f'搜索结果链接无效：{post["url"]}')
        for name in ['index.xml', 'sitemap.xml']:
            ET.parse(output / name)
        for name in ['robots.txt', '404.html', 'images/avatar.jpg', 'favicon.svg']:
            if not (output / name).is_file():
                errors.append(f'缺少文件：{name}')
    except (OSError, ValueError, KeyError, ET.ParseError) as error:
        errors.append(str(error))
    if errors:
        print('\n'.join(errors), file=sys.stderr)
        return 1
    print(f'通过：{len(files)} 个 HTML 页面、内部链接与锚点、{len(search)} 条搜索记录、RSS 和站点地图。')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
