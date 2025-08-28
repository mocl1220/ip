自动抓取公开的优选ip，获得ip.txt和ipv6.txt
==========================================

项目简介
--------

本项目通过自动化脚本 [`autoip6.py`](autoip6.py) 定时抓取多个公开源的 Cloudflare 优选 IPv4 和 IPv6 地址，并自动查询其所属国家，分别保存到 [`ip.txt`](ip.txt) 和 [`ipv6.txt`](ipv6.txt) 文件中。脚本支持去重、格式化输出，并通过 GitHub Actions 实现定时自动更新。

使用方法
--------

1. **本地运行**

   - 安装依赖：
     ```sh
     pip install requests ipaddress
     ```
   - 运行脚本：
     ```sh
     python autoip6.py
     ```
   - 运行后会在当前目录生成/更新 `ip.txt` 和 `ipv6.txt` 文件。
2. **自动化运行（推荐）**

   - 本项目已配置 [GitHub Actions](.github/workflows/autoip6.yml)，每小时自动抓取并更新 IP 文件，无需手动操作。

输出文件说明
------------

- `ip.txt`：每行格式为 `IPv4:8443#国家代码`，如 `104.16.47.90:8443#US`
- `ipv6.txt`：每行格式为 `[IPv6]:8443#国家代码-IPV6`，如 `[2a06:98c1:3120:c39b:7522:c680:d288:d13c]:8443#US-IPV6`

数据来源
--------

脚本会从多个公开 IP 源自动抓取数据，具体源见 [`autoip6.py`](autoip6.py) 文件中的 `urls` 列表。

注意事项
--------

- 国家代码通过 ipinfo.io 查询，若查询失败则标记为 `ZZ`。
- 若需自定义数据源或端口号，可修改 [`autoip6.py`](autoip6.py) 脚本。
