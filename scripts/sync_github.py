#!/usr/bin/env python3
"""Refresh public GitHub metadata at build time; visitors make no API calls."""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DESCRIPTIONS = {
    'easy-paper-reader': '将论文 PDF 整理成长篇中文解读，逐图解释，让贡献与实验证据对应。',
    'CornellLabelMain': '用于 Cornell 抓取数据集标注的 Python 脚本。',
    'tensorrtx': '保存使用的 TensorRTx 代码，基于 TensorRT API 构建深度学习网络。',
    'LoongForge': '面向语言、多模态与具身模型的模块化、高效训练框架。',
    'vision-based-robotic-grasping': '基于视觉的机器人抓取相关论文与代码。',
    'Image_weighing': '通过计算机视觉在线估计白羽北京鸭胴体重量的研究代码。',
    'Unlimited-OCR': '探索一次完成长篇文档解析的 OCR 项目。',
}


def get_json(url):
    headers = {'User-Agent': 'neverland-blog', 'Accept': 'application/vnd.github+json', 'X-GitHub-Api-Version': '2022-11-28'}
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f'Bearer {token}'
    request = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def main():
    parser = argparse.ArgumentParser(description='同步 GitHub 公开资料与仓库信息')
    parser.add_argument('--strict', action='store_true', help='网络异常时返回失败，不使用已有快照')
    args = parser.parse_args()
    destination = ROOT / 'data' / 'github.json'
    try:
        profile = get_json('https://api.github.com/users/NeverlanD0829')
        repos = []
        page = 1
        while True:
            batch = get_json(f'https://api.github.com/users/NeverlanD0829/repos?per_page=100&sort=updated&page={page}')
            repos.extend(batch)
            if len(batch) < 100:
                break
            page += 1
        keys = ['name', 'description', 'html_url', 'language', 'stargazers_count', 'fork', 'updated_at']
        result = {
            'fetched_at': datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'profile': {key: profile[key] for key in ['login', 'name', 'html_url', 'location', 'bio', 'public_repos']},
            'repos': [{**{key: repo[key] for key in keys}, 'description_zh': DESCRIPTIONS.get(repo['name'], '')} for repo in repos],
        }
        avatar_request = urllib.request.Request(profile['avatar_url'] + '&s=320', headers={'User-Agent': 'neverland-blog'})
        with urllib.request.urlopen(avatar_request, timeout=30) as response:
            avatar = response.read()
        if not avatar:
            raise ValueError('Avatar response was empty')
        destination.parent.mkdir(parents=True, exist_ok=True)
        avatar_path = ROOT / 'static' / 'images' / 'avatar.jpg'
        avatar_path.parent.mkdir(parents=True, exist_ok=True)
        avatar_path.write_bytes(avatar)
        temporary = destination.with_suffix('.tmp')
        temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        temporary.replace(destination)
        print(f'已同步 {profile["login"]} 的 {len(repos)} 个公开仓库与头像。')
    except (OSError, ValueError, KeyError, TypeError) as error:
        if args.strict or not destination.exists() or not (ROOT / 'static/images/avatar.jpg').exists():
            print(f'GitHub 同步失败：{error}', file=sys.stderr)
            return 1
        print(f'GitHub 同步暂不可用，保留已有公开资料快照：{error}', file=sys.stderr)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
