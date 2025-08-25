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

# 用于匹配 IP:端口 或 IP 的正则表达式
ip_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}(?::[0-9]{1,5})?\b'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def is_dynamic_page(text):
    return any(marker in text for marker in ['window.location.href', 'window.__CF$cv$params', '<noscript>'])

def fetch_static_content(url):
    try:
        print(f"尝试使用 requests 获取: {url}")
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        text = response.text
        if is_dynamic_page(text):
            return None
        return text
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ""

def fetch_rendered_content(url):
    print(f"切换至 requests-html 渲染: {url}")
    try:
        session = HTMLSession()
        r = session.get(url, headers=HEADERS, timeout=15)
        r.html.render(timeout=30)
        return r.html.full_text
    except Exception as e:
        print(f"Error rendering {url}: {e}")
        return ""

def process_text_to_ips(text):
    """处理文本，提取所有IP:端口或IP"""
    ip_set = set()
    for match in re.finditer(ip_pattern, text):
        ip_port = match.group(0)
        ip_set.add(ip_port)
    return list(ip_set)

def query_country(ip):
    """用api查询IP（不含端口）对应的国家名，出错则返回'未知'"""
    base_ip = ip.split(':')[0]
    try:
        url = f'https://ip9.com.cn/get?ip={base_ip}'
        resp = requests.get(url, timeout=8)
        data = resp.json()
        country = data.get('country', '') or data.get('country_name', '') or '未知'
        country = country.strip() or '未知'
        return country
    except Exception as e:
        print(f"查询IP {base_ip} 国家失败: {e}")
        return '未知'

def main():
    all_ips = set()
    urls_to_render = []

    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_url = {executor.submit(fetch_static_content, url): url for url in urls}
        for future in future_to_url:
            url = future_to_url[future]
            try:
                text = future.result()
                if text is None:
                    urls_to_render.append(url)
                else:
                    ips = process_text_to_ips(text)
                    all_ips.update(ips)
            except Exception as e:
                print(f"URL {url} generated an exception: {e}")

    for url in urls_to_render:
        text = fetch_rendered_content(url)
        if text:
            ips = process_text_to_ips(text)
            all_ips.update(ips)

    # 查询每个IP的国家，并格式化输出
    output_lines = []
    print(f"正在查询全部 {len(all_ips)} 个IP的国家信息...")
    with ThreadPoolExecutor(max_workers=8) as executor:
        ip_to_country = list(executor.map(query_country, all_ips))
    for ip_port, country in zip(all_ips, ip_to_country):
        output_lines.append(f"{ip_port}#{country}")

    output_file = 'ip_auto.txt'
    with open(output_file, 'w', encoding='utf-8') as f:
        for line in sorted(output_lines):
            f.write(line + '\n')
    print(f"Successfully wrote {len(output_lines)} IPs to {output_file}")

if __name__ == "__main__":
    main()
