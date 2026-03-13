# -*- coding: utf-8 -*-
"""
泰州菜价数据抓取脚本
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
from urllib.parse import urljoin
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def get_previous_workday():
    today = datetime.now()
    for i in range(1, 8):
        prev_day = today - timedelta(days=i)
        if prev_day.weekday() < 5:
            return prev_day
    return today - timedelta(days=1)

def scrape_vegetable_price():
    print("开始抓取菜价数据...")
    
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
    
    # 4. 保存为CSV
    df_result = pd.DataFrame(result, columns=["商品名称", "规格", "最低价"])
    df_result.to_csv("price.csv", index=False, encoding="utf-8-sig")
    
    # 5. 保存元数据
    with open("metadata.json", "w", encoding="utf-8") as f:
        f.write(f'{{"title": "{title}", "update_time": "{datetime.now().strftime("%Y-%m-%d %H:%M")}"}}')
    
    print(f"数据抓取完成！共 {len(result)} 条记录")
    print(f"标题: {title}")

if __name__ == "__main__":
    scrape_vegetable_price()
