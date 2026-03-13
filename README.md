# 泰州菜价数据抓取

## 本地运行

```bash
pip install -r requirements.txt
python scrape.py
```

## 部署到 Gitee Pages

1. 在 Gitee 创建仓库
2. 推送代码
3. 仓库 → 服务 → Gitee Pages → 启动

## 手动更新数据

```bash
python scrape.py
git add price.csv metadata.json
git commit -m "更新菜价数据"
git push
```

## 文件说明
- `scrape.py` - 数据抓取脚本
- `index.html` - 前端页面
- `price.csv` - 菜价数据
- `metadata.json` - 元数据
