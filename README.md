# 泰州菜价

泰州农贸市场菜价查询，每天自动更新。

## 部署

1. 创建 GitHub 仓库
2. 推送代码：`git push origin master`
3. 启用 GitHub Pages：Settings → Pages → Source: master branch

## 手动触发更新

在仓库的 Actions 页面点击 "Run workflow"

## 文件说明
- `scrape.py` - 数据抓取脚本
- `index.html` - 前端页面
- `price.csv` - 菜价数据（自动生成）
- `metadata.json` - 元数据（自动生成）
