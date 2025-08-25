import requests
from requests_html import HTMLSession
import re
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

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

def is_dynamic_page(text):
    """
    基于内容判断是否为动态加载的页面。
    如果文本很短，或包含特定JavaScript标记，则返回True。
    """
    # 检查是否包含JavaScript重定向或动态加载的标记
    if 'window.location.href' in text or 'window.__CF$cv$params' in text or '<noscript>' in text:
        return True
    
    # 如果内容很短，也可能是动态加载的
    if len(text.strip()) < 500:
        return True
        
    return False

def fetch_content_from_url(url):
    """
    智能地抓取URL内容，自动判断是否需要JavaScript渲染。
    """
    try:
        # 第一次尝试：使用requests获取静态内容
        print(f"尝试使用 requests 获取: {url}")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        text = response.text

        # 基于内容进行判断
        if is_dynamic_page(text):
            print(f"内容判断为动态页面，切换至 requests-html 渲染: {url}")
            # 如果是动态页面，则使用requests-html进行渲染
            session = HTMLSession()
            r = session.get(url, timeout=15)
            r.html.render(timeout=30)
            return r.html.full_text
        else:
            print(f"内容判断为静态页面，直接处理: {url}")
            return text

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return ""

def process_text_to_ips(text):
    """
    处理文本，提取并格式化IP地址。
    """
    ip_list = []
    matches = re.finditer(ip_pattern, text)
    for match in matches:
        full_match = match.group(0)
        country_code = match.group(1) if match.group(1) else 'US'
        formatted_ip = f"{full_match}#{country_code}"
        ip_list.append(formatted_ip)
    
    return ip_list

def main():
    """
    主函数，执行整个流程。
    """
    all_ips = set()
    with ThreadPoolExecutor(max_workers=8) as executor:
        future_to_url = {executor.submit(fetch_content_from_url, url): url for url in urls}
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                text = future.result()
                if text:
                    ips = process_text_to_ips(text)
                    for ip in ips:
                        all_ips.add(ip)
            except Exception as e:
                print(f"URL {url} generated an exception: {e}")

    output_file = 'ip_auto.txt'
    with open(output_file, 'w') as f:
        for ip in sorted(list(all_ips)):
            f.write(ip + '\n')
            
    print(f"Successfully wrote {len(all_ips)} IPs to {output_file}")

if __name__ == "__main__":
    main()
