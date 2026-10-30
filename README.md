# NeverlanD 的笔记

基于 [Hugo](https://gohugo.io/) 的个人静态博客，托管在 GitHub Pages：**https://neverland0829.github.io/**。

支持首页、文章、标签、归档、项目、关于、全文搜索、深浅主题、文章目录、代码复制、RSS 和移动端适配。数据来自 [GitHub](https://github.com/NeverlanD0829)，无需数据库。

## 本地预览

安装 [Hugo](https://gohugo.io/installation/)（版本见 `.hugo-version`），然后：

```bash
hugo server -D
```

访问 http://localhost:1313/ 即可。`-D` 包含草稿，仅本地预览用。

## 写文章

每篇文章在 `content/posts/` 下建一个目录，例如 `content/posts/my-first-post/index.md`，头部加：

```markdown
---
title: '我的第一篇笔记'
date: 2026-10-30T12:00:00+08:00
draft: false
slug: my-first-post
description: '一句话介绍这篇文章。'
tags: ['技术笔记']
---

正文从这里开始。
```

也可以建草稿：`python3 scripts/new_post.py my-first-post "我的第一篇笔记"`。

`draft: true` 的文章不会发布，也不进搜索、RSS 和站点地图；未来日期的文章到了日期重新构建才会出现。

## 发布

推送到 `main` 分支自动构建发布（GitHub Actions）：

```bash
git add .
git commit -m "update"
git push origin main
```

发布进度和日志在仓库 **Actions** 标签页查看。

## 修改个人资料

| 想改的内容 | 文件 |
| --- | --- |
| 标题、描述、邮箱、位置、技术栈、精选项目 | `hugo.toml` |
| 首页介绍文案 | `layouts/index.html` |
| 完整个人介绍 | `content/about/index.md` |
| 文章 | `content/posts/` |
| 主题颜色、排版、移动端样式 | `assets/css/main.css` |

更新公开仓库数据与头像：`python3 scripts/sync_github.py`（只读公开数据，成功后提交 `data/github.json` 和 `static/images/avatar.jpg`）。