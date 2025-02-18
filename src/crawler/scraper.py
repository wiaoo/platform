
import requests
from bs4 import BeautifulSoup
import json
import time
import re
from pathlib import Path

# 配置文件路径
DATA_DIR = Path('../../data')
SHOPS_FILE = DATA_DIR / 'shops.json'
SALES_FILE = DATA_DIR / 'sales.json'
TOTAL_FILE = DATA_DIR / 'total_shops.json'

# 初始化数据目录
DATA_DIR.mkdir(exist_ok=True)


def load_data(file_path):
    """加载JSON数据"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_data(data, file_path):
    """保存数据到JSON"""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)


def get_headers():
    """生成随机请求头"""
    return {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept-Language': 'en-US,en;q=0.9',
    }


def fetch_total_shops():
    """获取总店铺数量"""
    url = 'https://www.etsy.com/search/shops?search_query=+'
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        count_tag = soup.find('strong', string=re.compile(r'\d'))
        if count_tag:
            return int(re.sub(r'\D', '', count_tag.text))
    except Exception as e:
        print(f"获取总店铺数失败: {str(e)}")
    return None


def fetch_shop_sales(shop_url):
    """获取单个店铺销量"""
    try:
        response = requests.get(shop_url, headers=get_headers(), timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        sales_tag = soup.find('a', {'href': re.compile(r'/sold')})
        if sales_tag:
            match = re.search(r'(\d+,?\d+)', sales_tag.text)
            return int(match.group(1).replace(',', '')) if match else None
    except Exception as e:
        print(f"获取 {shop_url} 销量失败: {str(e)}")
    return None


def main():
    # 加载店铺列表
    shops = load_data(SHOPS_FILE) or [
        "https://www.etsy.com/shop/LuckyPlumStudio",
        "https://www.etsy.com/shop/AnotherExampleShop"
    ]

    # 采集总店铺数
    total = fetch_total_shops()
    if total is not None:
        total_data = load_data(TOTAL_FILE)
        total_data.append({
            'timestamp': int(time.time()),
            'total_shops': total
        })
        save_data(total_data, TOTAL_FILE)
        print(f"更新总店铺数: {total}")

    # 采集各店铺销量
    sales_data = load_data(SALES_FILE)
    for shop_url in shops:
        sales = fetch_shop_sales(shop_url)
        if sales is not None:
            sales_data.append({
                'timestamp': int(time.time()),
                'shop_url': shop_url,
                'sales': sales
            })
            print(f"{shop_url} 销量: {sales}")
        time.sleep(5)  # 请求间隔

    save_data(sales_data, SALES_FILE)


if __name__ == "__main__":
    main()
    print("数据已保存到data目录")