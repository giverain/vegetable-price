# -*- coding: utf-8 -*-
"""
泰州菜价自动抓取 + 网页展示
功能：每日自动更新，浏览器打开即看最低价表格
"""
from flask import Flask, render_template_string
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from datetime import datetime, timedelta
import threading
import time
from urllib.parse import urljoin

app = Flask(__name__)

# 全局变量：保存最新菜价数据
latest_data = {
    "article_title": "",
    "update_time": "未更新",
    "price_table": []
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# ---------------------- 1. 抓取并更新数据 ----------------------
def update_vegetable_price():
    """每日自动更新菜价数据"""
    try:
        print("开始更新菜价...")
        # 1. 获取最新文章链接
        list_url = "https://fgw.taizhou.gov.cn/jgxx/mswj/nmsc/index.html"
        resp = requests.get(list_url, headers=HEADERS, timeout=15)
        resp.encoding = "utf-8"
        soup = BeautifulSoup(resp.text, "html.parser")
        iframe = soup.find("iframe", src=True)
        if iframe:
            iframe_url = iframe["src"]
            if not iframe_url.startswith("http"):
                iframe_url = "https://fgw.taizhou.gov.cn" + iframe_url
            resp = requests.get(iframe_url, headers=HEADERS, timeout=15)
            resp.encoding = "utf-8"
            soup = BeautifulSoup(resp.text, "html.parser")
        
        # 计算前一个工作日
        def get_previous_workday():
            today = datetime.now()
            for i in range(1, 8):
                prev_day = today - timedelta(days=i)
                if prev_day.weekday() < 5:
                    return prev_day
            return today - timedelta(days=1)
        
        target_date = get_previous_workday()
        month = target_date.month
        day = target_date.day
        target_date_str = f"{month}月{day}日"
        
        articles = soup.find_all("a", string=re.compile("食品价格监测行情"))
        if not articles:
            raise Exception("未找到菜价文章")
        
        target_article = None
        for article in articles:
            title = article.get_text(strip=True)
            if target_date_str in title:
                target_article = article
                break
        
        if not target_article:
            target_article = articles[0]
        
        if not target_article:
            target_article = articles[0]
        
        title = target_article.get_text(strip=True)
        title = title.lstrip('\u3000\u00a0\s')
        link = target_article["href"]
        link = urljoin("https://fgw.taizhou.gov.cn/spfgs/liebiao1/", link)

        # 2. 解析价格表格
        resp2 = requests.get(link, headers=HEADERS, timeout=15)
        resp2.encoding = "utf-8"
        soup2 = BeautifulSoup(resp2.text, "html.parser")
        tables = soup2.find_all("table")
        if len(tables) < 4:
            raise Exception("未找到价格表格")
        target_table = tables[3]
        df = pd.read_html(str(target_table))[0]

        # 3. 计算最低价
        result = []
        for _, row in df.iterrows():
            veg_name = str(row.iloc[1]).strip()
            if not veg_name or "、" in veg_name or veg_name.startswith("一、") or veg_name.startswith("二、"):
                continue
            
            spec = str(row.iloc[2]).strip() if pd.notna(row.iloc[2]) else ""
            
            prices = []
            for i in [5,6,7,8]:
                try:
                    val = row.iloc[i]
                    if pd.isna(val) or val == '':
                        continue
                    p = float(str(val).replace("元","").strip())
                    prices.append(p)
                except:
                    continue
            if prices:
                min_price = round(min(prices) * 2, 2)
                result.append([veg_name, spec, min_price])

        # 4. 更新全局数据
        global latest_data
        latest_data["article_title"] = title
        latest_data["update_time"] = datetime.now().strftime('%Y-%m-%d %H:%M')
        latest_data["price_table"] = result
        print("菜价更新完成！")
    
    except Exception as e:
        print(f"更新失败：{str(e)}")

# ---------------------- 2. 网页展示页面 ----------------------
@app.route('/')
def show_price():
    # 网页模板（纯HTML表格，美观简洁）
    html_template = """
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>泰州农贸市场菜价最低价</title>
        <style>
            body{font-family:'Microsoft YaHei',微软雅黑,Arial,sans-serif; margin:0; padding:0; background:#fff; min-height:100vh;}
            .container{max-width:100%; margin:0 auto; padding:15px; box-sizing:border-box;}
            .update{color:#666; text-align:center; margin-bottom:20px; font-size:14px;}
            .discount-box{padding:15px; text-align:center; border-bottom:1px solid #eee;}
            .discount-box label{font-size:14px; font-weight:bold; color:#333; margin-right:8px;}
            .discount-box input{width:100px; padding:8px 12px; font-size:16px; border:2px solid #ddd; border-radius:8px; text-align:center;}
            .table-wrapper{overflow-x:auto; -webkit-overflow-scrolling:touch;}
            table{width:100%; border-collapse:collapse; margin:0 auto; background:#fff;}
            th,td{padding:4px 2px; text-align:center; border:1px solid #ddd; font-size:13px;}
            th{background:#f8f9fa; color:#333; font-weight:bold;}
            th .unit{font-size:10px; color:#999; font-weight:normal;}
            tr:hover{background:#f5f5f5;}
            .original-price{color:#333;}
            .discounted-price{color:#333; font-weight:bold;}
            .spec{color:#999; font-size:11px;}
            .article-title{font-size:16px; font-weight:bold; margin-bottom:5px; color:#000;}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="update">
                <div class="article-title">{{ article_title }}</div>
                <div>更新时间：{{ update_time }}</div>
            </div>
            <div class="discount-box">
                <label>折扣：</label>
                <input type="number" step="0.01" min="0" max="1" value="0.8" placeholder="0.8" id="discount" oninput="applyDiscount()">
            </div>
            <div class="table-wrapper">
            <table>
                <tr>
                    <th>序号</th>
                    <th>商品名称</th>
                    <th>最低价<br><span class="unit">（元/千克）</span></th>
                    <th>折后价<br><span class="unit">（元/千克）</span></th>
                </tr>
            {% for item in price_list %}
            <tr>
                <td>{{ loop.index }}</td>
                <td>{{ item[0] }}<br><span class="spec">{{ item[1] }}</span></td>
                <td class="original-price">{{ item[2] }}</td>
                <td class="discounted-price">{{ item[2] }}</td>
            </tr>
            {% endfor %}
        </table>
        </div>
        <script>
            function applyDiscount() {
                var discount = parseFloat(document.getElementById('discount').value);
                if (isNaN(discount) || discount < 0 || discount > 1) {
                    return;
                }
                var prices = document.querySelectorAll('.discounted-price');
                prices.forEach(function(td) {
                    var original = parseFloat(td.getAttribute('data-original'));
                    if (isNaN(original)) {
                        original = parseFloat(td.innerText);
                        td.setAttribute('data-original', original);
                    }
                    td.innerText = (original * discount).toFixed(2);
                });
            }
            window.onload = applyDiscount;
        </script>
    </body>
    </html>
    """
    return render_template_string(
        html_template,
        article_title=latest_data.get("article_title", ""),
        update_time=latest_data["update_time"],
        price_list=latest_data["price_table"]
    )

# ---------------------- 3. 启动时自动更新一次 ----------------------
def first_run():
    update_vegetable_price()

# ---------------------- 4. 云函数入口 ----------------------
def handler(event, context):
    """云函数 SCF 入口"""
    app.run(host="0.0.0.0", port=9000)

if __name__ == "__main__":
    first_run()
    # 本地测试用
    app.run(host="0.0.0.0", port=5000, debug=True)