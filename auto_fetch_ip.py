import requests
from requests_html import HTMLSession
import re
import os
from concurrent.futures import ThreadPoolExecutor

# 要抓取的URL列表
urls = [
    'https://ip.164746.xyz',
    'https://cf.090227.xyz',
    'https://stock.hostmonit.com/CloudFlareYes',
    'https://ip.164746.xyz/',
    'https://ipdb.api.030101.xyz/?type=bestcf&country=true',
    'https://addressesapi.090227.xyz/ip.164746.xyz',
    'https://addressesapi.090227.xyz/CloudFlareYes',
    'https://www.wetest.vip/page/cloudflare/address_v4.html'
]

# 用于匹配 IP 地址的正则表达式
ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?::[0-9]{1,5})?(?:#([A-Z]{2}))?\b'

# 添加伪造的User-Agent头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def is_dynamic_page(text):
    """
    基于内容判断是否为动态加载的页面。
    只在包含特定JS标记时才返回True。
    """
    # 检查是否包含JavaScript重定向或动态加载的标记
    return any(marker in text for marker in ['window.location.href', 'window.__CF$cv$params', '<noscript>'])

def fetch_static_content(url):
    """使用requests获取静态内容。"""
    try:
        print(f"尝试使用 requests 获取: {url}")
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        text = response.text
        if is_dynamic_page(text):
            return None # 返回None，表示需要渲染
        return text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ""

def fetch_rendered_content(url):
    """使用requests-html渲染动态页面。"""
    print(f"切换至 requests-html 渲染: {url}")
    try:
        session = HTMLSession()
        r = session.get(url, headers=HEADERS, timeout=15)
        # 强制渲染，timeout确保不会无限等待
        r.html.render(timeout=30)
        return r.html.full_text
    except Exception as e:
        print(f"Error rendering {url}: {e}")
        return ""

def process_text_to_ips(text):
    """处理文本，提取并格式化IP地址。"""
    ip_list = []
    # 查找所有匹配的IP地址模式
    matches = re.finditer(ip_pattern, text)
    for match in matches:
        full_match = match.group(0)
        country_code = match.group(1) if match.group(1) else 'US'
        formatted_ip = f"{full_match}#{country_code}"
        ip_list.append(formatted_ip)
    return ip_list

def main():
    """主函数，执行整个流程。"""
    all_ips = set()
    urls_to_render = []

    # 1. 使用线程池并发获取所有URL的静态内容
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_url = {executor.submit(fetch_static_content, url): url for url in urls}
        for future in future_to_url:
            url = future_to_url[future]
            try:
                text = future.result()
                if text is None:
                    # 如果返回None，说明需要渲染，加入渲染列表
                    urls_to_render.append(url)
                else:
                    ips = process_text_to_ips(text)
                    for ip in ips:
                        all_ips.add(ip)
            except Exception as e:
                print(f"URL {url} generated an exception: {e}")

    # 2. 顺序处理需要渲染的URL
    for url in urls_to_render:
        text = fetch_rendered_content(url)
        if text:
            ips = process_text_to_ips(text)
            for ip in ips:
                all_ips.add(ip)

    # 将IP地址写入文件
    output_file = 'ip_auto.txt'
    with open(output_file, 'w') as f:
        for ip in sorted(list(all_ips)):
            f.write(ip + '\n')
    print(f"Successfully wrote {len(all_ips)} IPs to {output_file}")

if __name__ == "__main__":
    main()
