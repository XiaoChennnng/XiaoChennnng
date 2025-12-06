#!/usr/bin/env python3
"""
GitHub README 自动更新脚本
用于自动获取GitHub统计数据并更新README.md
"""

import os
import re
from github import Github
from datetime import datetime

# GitHub Token（从环境变量获取）
TOKEN = os.getenv('GITHUB_TOKEN')
USERNAME = 'XiaoChennnng'

def get_github_data():
    """获取GitHub用户数据"""
    g = Github(TOKEN)
    user = g.get_user(USERNAME)

    # 获取基本信息
    public_repos = user.public_repos
    followers = user.followers

    # 获取总Stars数和提交数
    total_stars = 0
    total_commits = 0
    total_prs = 0
    total_issues = 0

    repos = user.get_repos(sort='updated', direction='desc')

    for repo in repos:
        total_stars += repo.stargazers_count

        # 修复：统计**该用户在该仓库的提交数**，而不是整个仓库的提交数
        try:
            user_commits = repo.get_commits(author=USERNAME).totalCount
            total_commits += user_commits if user_commits else 0
        except Exception as e:
            print(f"⚠️ 获取 {repo.name} 的用户提交数失败: {e}")
            total_commits += 0

        # 修复：统计该用户创建的PR和Issue
        try:
            user_prs = repo.get_pulls(state='closed', creator=USERNAME).totalCount + repo.get_pulls(state='open', creator=USERNAME).totalCount
            total_prs += user_prs if user_prs else 0
        except Exception:
            pass

        try:
            user_issues = repo.get_issues(state='closed', creator=USERNAME).totalCount + repo.get_issues(state='open', creator=USERNAME).totalCount
            total_issues += user_issues if user_issues else 0
        except Exception:
            pass

    return {
        'public_repos': public_repos,
        'followers': followers,
        'total_stars': total_stars,
        'total_commits': total_commits,
        'total_prs': total_prs,
        'total_issues': total_issues,
    }

def get_latest_repos(limit=5):
    """获取最新更新的仓库"""
    g = Github(TOKEN)
    user = g.get_user(USERNAME)

    repos = []
    for repo in user.get_repos(sort='updated', direction='desc'):
        if not repo.fork:  # 跳过fork的仓库
            repos.append({
                'name': repo.name,
                'description': repo.description or '暂无描述',
                'language': repo.language or 'N/A',
                'stars': repo.stargazers_count,
                'url': repo.html_url,
            })
        if len(repos) >= limit:
            break

    return repos

def generate_achievements_section(data):
    """生成成就section内容"""
    content = """<div align="center">

| 🎯 成就 | 数据 |
|--------|------|
| 📦 公开仓库 | {} |
| ⭐ 总获得Stars | {} |
| 👥 Followers | {} |
| 📝 总提交数 | {} |
| 🔀 Pull Requests | {} |
| 🐛 Issues | {} |

</div>"""

    return content.format(
        data['public_repos'],
        data['total_stars'],
        data['followers'],
        data['total_commits'],
        data['total_prs'],
        data['total_issues'],
    )

def generate_repos_section(repos):
    """生成最新项目section内容"""
    if not repos:
        return """<div align="center">

| 项目名称 | 描述 | 语言 | Stars |
|--------|------|------|-------|
| 暂无项目 | 开始创建你的第一个项目吧 | - | 0 |

</div>"""

    rows = []
    for repo in repos:
        rows.append(f"| [{repo['name']}]({repo['url']}) | {repo['description'][:30]}... | {repo['language']} | ⭐ {repo['stars']} |")

    content = """<div align="center">

| 项目名称 | 描述 | 语言 | Stars |
|--------|------|------|-------|
{}

</div>"""

    return content.format('\n'.join(rows))

def update_readme():
    """更新README.md文件"""
    readme_path = 'README.md'

    # 读取README内容
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 获取数据
    print("正在获取GitHub数据...")
    try:
        github_data = get_github_data()
        latest_repos = get_latest_repos()

        # 生成新的sections
        achievements = generate_achievements_section(github_data)
        repos = generate_repos_section(latest_repos)

        # 更新achievements section
        pattern_achievements = r'<!--START_SECTION:achievements-->.*?<!--END_SECTION:achievements-->'
        new_achievements = f'<!--START_SECTION:achievements-->\n{achievements}\n<!--END_SECTION:achievements-->'
        content = re.sub(pattern_achievements, new_achievements, content, flags=re.DOTALL)

        # 更新latest-repos section
        pattern_repos = r'<!--START_SECTION:latest-repos-->.*?<!--END_SECTION:latest-repos-->'
        new_repos = f'<!--START_SECTION:latest-repos-->\n{repos}\n<!--END_SECTION:latest-repos-->'
        content = re.sub(pattern_repos, new_repos, content, flags=re.DOTALL)

        # 写入更新后的内容
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print("✅ README.md 更新成功!")
        return True

    except Exception as e:
        print(f"❌ 更新失败: {e}")
        return False

if __name__ == '__main__':
    if not TOKEN:
        print("❌ 错误: 未找到 GITHUB_TOKEN 环境变量")
        exit(1)

    success = update_readme()
    exit(0 if success else 1)
