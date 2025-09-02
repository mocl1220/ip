import requests
import re
import os
import time
import ipaddress

# 目标URL列表
urls = [
    'https://ip.164746.xyz', 
    'https://api.uouin.com/cloudflare.html',
    'https://ipdb.api.030101.xyz/?type=bestcf&country=true',
    'https://addressesapi.090227.xyz/CloudFlareYes',
    'https://raw.githubusercontent.com/ymyuuu/IPDB/main/BestCF/bestcfv4.txt',
    'https://www.wetest.vip/page/cloudflare/address_v6.html',
    'https://www.wetest.vip/page/cloudflare/address_v4.html'
]
#    'https://cf.090227.xyz', 
#    'https://stock.hostmonit.com/CloudFlareYes',
#    'https://addressesapi.090227.xyz/ip.164746.xyz',

# 正则表达式用于初步匹配IPV4与IPV6地址（配合ipaddress库二次过滤）
ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
ipv6_pattern = r'\b(?:[A-F0-9a-f]{1,4}:){1,7}[A-F0-9a-f]{1,4}\b'  # 加入小写支持

# 检查ip.txt和ipv6.txt文件是否存在,如果存在则删除它
if os.path.exists('ip.txt'):
    os.remove('ip.txt')
if os.path.exists('ipv6.txt'):
    os.remove('ipv6.txt')

# 使用集合存储IP地址实现自动去重
unique_ipv4 = set()
unique_ipv6 = set()

for url in urls:
    try:
        # 发送HTTP请求获取网页内容
        response = requests.get(url, timeout=7)
        
        # 确保请求成功
        if response.status_code == 200:
            # 获取网页的文本内容
            html_content = response.text
            
            # 使用正则表达式查找IP地址
            ipv4_matches = re.findall(ipv4_pattern, html_content)
            ipv6_matches = re.findall(ipv6_pattern, html_content)
            
            # 用ipaddress校验并去重
            for ip in ipv4_matches:
                try:
                    ipaddress.IPv4Address(ip)
                    unique_ipv4.add(ip)
                except ValueError:
                    continue
            for ip in ipv6_matches:
                try:
                    # 粗略过滤后进一步用ipaddress校验
                    ip_obj = ipaddress.IPv6Address(ip)
                    unique_ipv6.add(ip.lower())
                except ValueError:
                    continue
    except requests.exceptions.RequestException as e:
        print(f'请求 {url} 失败: {e}')
        continue

# 查询每个IP的country_code
def get_country_code(ip):
    try:
        url = f'https://api.ipinfo.io/lite/{ip}?token=6f75ff6b8f013b'
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            return data.get('country_code') or data.get('country') or 'ZZ'
        else:
            return 'ZZ'
    except Exception as e:
        print(f"查询IP {ip} country_code失败: {e}")
        return 'ZZ'

if unique_ipv4:
    sorted_ipv4 = sorted(unique_ipv4, key=lambda ip: [int(part) for part in ip.split('.')])
    results_v4 = []
    for ip in sorted_ipv4:
        country_code = get_country_code(ip)
        results_v4.append(f"{ip}:8443#{country_code}")
        time.sleep(1)
    with open('ip.txt', 'w', encoding='utf-8') as file:
        for line in results_v4:
            file.write(line + '\n')
    print(f'已保存 {len(results_v4)} 个唯一IPv4地址及country_code到ip.txt文件。')
else:
    print('未找到有效的IPv4地址。')

if unique_ipv6:
    sorted_ipv6 = sorted(unique_ipv6)
    results_v6 = []
    for ip in sorted_ipv6:
        country_code = get_country_code(ip)
        results_v6.append(f"[{ip}]:8443#{country_code}-IPV6")
        time.sleep(1)
    with open('ipv6.txt', 'w', encoding='utf-8') as file:
        for line in results_v6:
            file.write(line + '\n')
    print(f'已保存 {len(results_v6)} 个唯一IPv6地址及country_code到ipv6.txt文件。')
else:
    print('未找到有效的IPv6地址。')
