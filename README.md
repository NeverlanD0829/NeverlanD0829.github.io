# NeverlanD 的笔记

基于 Hugo 的个人静态博客。参考 dyedd.cn 的简洁笔记风格，使用独立实现的模板与样式，个人资料来自 [NeverlanD0829 的 GitHub](https://github.com/NeverlanD0829)。

具备首页、文章、标签、归档、项目、关于、全文搜索、深浅主题、文章目录、代码复制、RSS、站点地图和移动端适配。访问网站不需要数据库、登录服务或 GitHub API；头像、样式、脚本和搜索索引均在站内。

## GitHub Pages 发布

站点地址：**https://neverland0829.github.io/**。源码仓库是 [NeverlanD0829.github.io](https://github.com/NeverlanD0829/NeverlanD0829.github.io)，由 GitHub Actions 构建并发布。下面是首次配置或重新部署时的步骤。

1. 在自己的 GitHub 账户下新建 **公开仓库**，名称必须是 `NeverlanD0829.github.io`。不要勾选初始化 README；如果这个仓库已经存在，先检查并备份已有内容，不要覆盖。
2. 在本项目目录提交并推送代码：

   ```bash
   git add .
   git commit -m "Create personal blog"
   git remote add origin https://github.com/NeverlanD0829/NeverlanD0829.github.io.git
   git push -u origin main
   ```

   本地已初始化 `main` 分支。如使用 ZIP 副本，先执行 `git init -b main`。Git 需要配置你自己的提交姓名、邮箱，并通过自己的 GitHub 凭据完成推送；不要把访问令牌写入项目文件。

3. 打开仓库 **Settings → Pages → Build and deployment → Source**，选择 **GitHub Actions**。
4. 在 **Actions → Build and deploy blog → Run workflow** 手动运行一次。成功后访问上面的地址。第一次推送如果发生在第 3 步之前，部署可能失败，设置完成后重跑即可。

后续推送到 `main` 会自动发布；每周一也会刷新公开项目数据再发布。拉取请求只构建和检查，不发布。工作流自动提供的 `GITHUB_TOKEN` 用于读取公开数据，不需要另建个人访问令牌或配置秘密。

发布进度和失败日志可以在仓库的 **Actions** 标签页查看。重新运行发布任务不会修改文章源码。

## 以后怎样写文章

最方便的方式是直接在 GitHub 网页打开仓库：**Add file → Create new file**，文件名写 `content/posts/my-first-post/index.md`，填入：

```markdown
---
title: '我的第一篇笔记'
date: 2026-10-30T12:00:00+08:00
draft: false
slug: my-first-post
description: '这里写一两句话，作为列表中的文章介绍。'
tags: ['技术笔记']
---

从这里开始写正文。

## 一个小标题

记录你的想法。
```

把日期替换为实际发表时间。文件路径和 `slug` 使用小写英文、数字及连字符。提交后 Actions 会生成网站；未来日期的文章到日期之后重新构建才会出现。`draft: true` 的文章不会发布，也不会进入搜索、RSS 或站点地图。

也可以在电脑上创建草稿：

```bash
python3 scripts/new_post.py my-first-post "我的第一篇笔记"
```

每篇文章放在自己的目录，图片可以放在同一目录后引用：`![图片说明](figure.png)`。文章目录由二、三级标题自动生成；代码块可使用三个反引号加语言名。

`content/posts/paper-notes-template/index.md` 是默认不发布的论文笔记模板。已经发布的两篇文章是根据公开资料整理的开站初稿，你可以直接修改或删除。

## 本地预览

安装 [Hugo](https://gohugo.io/installation/)，本项目验证版本记录在 `.hugo-version`，当前为 **0.169.0**，标准版即可。发布和数据同步脚本需要 **Python 3.11 或更新版本**，没有额外 Python 依赖。

```bash
hugo server -D
```

浏览器访问 http://localhost:1313/。`-D` 包含草稿，仅用于本地预览。

构建正式站点并检查内部链接：

```bash
hugo --gc --minify --cleanDestinationDir --panicOnWarning
python3 scripts/check_site.py
```

生成的 `public/` 可以部署到任何静态托管服务，不需要运行 Hugo 服务。

## 修改个人资料和项目

| 想修改的内容 | 文件 |
| --- | --- |
| 博客标题、描述、邮箱、位置、技术栈、精选项目 | `hugo.toml` |
| 首页介绍文案 | `layouts/index.html` |
| 完整个人介绍 | `content/about/index.md` |
| 博客文章 | `content/posts/` |
| 项目数据快照 | `data/github.json` |
| 仓库介绍的中文整理 | `scripts/sync_github.py` 中的 `DESCRIPTIONS` |
| 主题颜色、排版、移动端样式 | `assets/css/main.css` |

更新公开仓库数据与头像：

```bash
python3 scripts/sync_github.py
```

同步脚本只读取公开个人资料、公开仓库和头像。Fork 单独显示，不作为原创项目；`tensorrtx` 按仓库说明注明为保存使用的代码。个人简介、邮箱与技术栈来自公开 Profile README，保留为可编辑文案，不会被同步脚本覆盖。

离线时正常构建会使用已保存的数据。同步网络失败也会保留旧快照；想要求同步必须成功时使用 `--strict`。运行后如果想将新数据保存到源码版本中，再提交 `data/github.json` 和 `static/images/avatar.jpg`。

## 以后绑定自己的域名

域名注册完成后：

1. 在仓库 **Settings → Pages → Custom domain** 填入你的域名。
2. 按 [GitHub Pages 官方域名配置](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site) 添加相应的 DNS 记录，并开启 **Enforce HTTPS**。
3. 把 `hugo.toml` 的 `baseURL` 改成完整的 `https://你的域名/`，提交后重新部署。

本项目使用 GitHub Actions 发布，域名设置以 Pages 后台为准。更换域名后重建会同步更新 canonical、RSS 和站点地图。

## 文件结构

```text
hugo.toml                 站点配置
content/                  Markdown 文章与页面
layouts/                  Hugo 模板
assets/                   样式与浏览器脚本
static/                   头像、图标与其他静态文件
data/github.json          GitHub 公开资料快照
scripts/new_post.py        创建草稿
scripts/sync_github.py     同步公开资料
scripts/check_site.py      验证生成站点
.github/workflows/         自动构建和发布
```

文章和个人内容的版权归作者；其他仓库的说明、名称与素材保留其原有归属。项目未添加第三方评论、统计或广告服务。
