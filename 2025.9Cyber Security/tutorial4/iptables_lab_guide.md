# IPTables 防火墙配置实验指南 - Linux虚拟机版

## 🖥️ Linux虚拟机实验环境说明

### 实验环境优势
1. **安全的实验环境**：虚拟机环境相对安全，即使配置错误也不会影响主机系统
2. **快照功能**：可以创建虚拟机快照，方便实验前后对比和错误恢复
3. **网络隔离**：虚拟机网络相对独立，降低了网络安全风险
4. **便于重置**：可以随时重置虚拟机到初始状态

### 实验前准备
1. **创建虚拟机快照**：实验前建议创建虚拟机快照以便恢复
2. **确保网络连接**：检查虚拟机网络配置正常
3. **准备多个终端**：建议开启多个终端窗口进行测试
4. **了解虚拟机网络**：熟悉虚拟机的网络接口名称（如eth0、ens33等）

### 预备命令
```bash
# 更新系统包管理器
sudo apt update

# 安装必要工具（根据发行版选择）
# Ubuntu/Debian系统：
sudo apt install iptables-persistent netfilter-persistent

# CentOS/RHEL系统：
# sudo yum install iptables-services
# 或者 sudo dnf install iptables-services

# 备份当前规则
sudo iptables-save > ~/iptables_backup.rules

# 查看当前网络接口
ip addr show
# 或者使用传统命令
ifconfig

# 检查虚拟机网络连通性
ping -c 3 8.8.8.8

# 可选：启动screen会话（便于管理多个终端）
screen -S iptables_lab
```

## 实验步骤详解

### 准备阶段：清理环境
```bash
# 切换到root用户
sudo su

# 清理所有规则并设置宽松策略
iptables -P INPUT ACCEPT
iptables -P OUTPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -F
iptables -X
iptables -t nat -F
iptables -t nat -X
iptables -t mangle -F
iptables -t mangle -X

# 查看清理后的状态
iptables -vL -n
```

### 规则1：设置默认策略
**目标**：将输入策略设为DROP，输出策略设为ACCEPT

**💡 虚拟机环境说明**：在虚拟机中实验相对安全，但仍建议保持谨慎

```bash
# Before状态记录
echo "=== BEFORE Rule 1 ===" > ~/lab_log.txt
iptables -vL -n >> ~/lab_log.txt
ss -tuln >> ~/lab_log.txt

# 如果使用SSH连接虚拟机，先确保SSH端口开放
# iptables -A INPUT -p tcp --dport 22 -j ACCEPT
# iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# 设置默认策略
iptables -P INPUT DROP
iptables -P OUTPUT ACCEPT

# After状态记录
echo "=== AFTER Rule 1 ===" >> ~/lab_log.txt
iptables -vL -n >> ~/lab_log.txt

# 测试连接（在另一个终端或虚拟机控制台测试）
# ping google.com  # 应该失败
# curl http://www.baidu.com  # 应该失败
```

### 规则2：允许环回通信
```bash
# Before状态
echo "=== BEFORE Rule 2 ===" >> ~/lab_log.txt
iptables -vL -n >> ~/lab_log.txt

# 允许环回接口
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# After状态
echo "=== AFTER Rule 2 ===" >> ~/lab_log.txt
iptables -vL -n >> ~/lab_log.txt

# 测试
ping -c 3 127.0.0.1  # 应该成功
```

### 规则3：允许ICMP(ping)
```bash
# Before状态
echo "=== BEFORE Rule 3 ===" >> ~/lab_log.txt
iptables -vL -n >> ~/lab_log.txt

# 允许ICMP
iptables -A INPUT -p icmp -j ACCEPT
iptables -A OUTPUT -p icmp -j ACCEPT

# After状态
echo "=== AFTER Rule 3 ===" >> ~/lab_log.txt
iptables -vL -n >> ~/lab_log.txt

# 测试
ping -c 3 8.8.8.8  # 应该成功
ping -c 3 baidu.com  # 可能失败（需要DNS）
```

### 规则4：允许出站Web访问
```bash
# Before状态
echo "=== BEFORE Rule 4 ===" >> ~/lab_log.txt
iptables -vL -n >> ~/lab_log.txt

# 允许HTTP和HTTPS出站
iptables -A OUTPUT -p tcp --dport 80 -j ACCEPT
iptables -A OUTPUT -p tcp --dport 443 -j ACCEPT
iptables -A INPUT -p tcp --sport 80 -m state --state ESTABLISHED -j ACCEPT
iptables -A INPUT -p tcp --sport 443 -m state --state ESTABLISHED -j ACCEPT

# After状态
echo "=== AFTER Rule 4 ===" >> ~/lab_log.txt
iptables -vL -n >> ~/lab_log.txt

# 测试
curl -I http://www.baidu.com  # 可能仍失败（需要DNS）
curl -I https://www.baidu.com  # 可能仍失败（需要DNS）
curl -I http://220.181.38.148  # 使用IP测试
```

### 规则5：启用DNS
```bash
# Before状态
echo "=== BEFORE Rule 5 ===" >> ~/lab_log.txt
iptables -vL -n >> ~/lab_log.txt

# 允许DNS查询（UDP 53端口）
iptables -A OUTPUT -p udp --dport 53 -j ACCEPT
iptables -A INPUT -p udp --sport 53 -m state --state ESTABLISHED -j ACCEPT

# 也允许TCP DNS（某些查询需要）
iptables -A OUTPUT -p tcp --dport 53 -j ACCEPT
iptables -A INPUT -p tcp --sport 53 -m state --state ESTABLISHED -j ACCEPT

# After状态
echo "=== AFTER Rule 5 ===" >> ~/lab_log.txt
iptables -vL -n >> ~/lab_log.txt

# 测试
nslookup baidu.com  # 应该成功
curl -I http://www.baidu.com  # 现在应该成功
```

### 规则6：阻止特定网站
```bash
# Before状态
echo "=== BEFORE Rule 6 ===" >> ~/lab_log.txt
iptables -vL -n >> ~/lab_log.txt

# 选择要阻止的网站（例如：facebook.com）
# 首先查找IP地址
nslookup facebook.com

# 阻止特定IP（替换为实际IP）
iptables -I OUTPUT -d 157.240.241.35 -j DROP

# 或者阻止域名（需要额外模块）
# iptables -I OUTPUT -p tcp --dport 80 -m string --string "facebook.com" --algo bm -j DROP
# iptables -I OUTPUT -p tcp --dport 443 -m string --string "facebook.com" --algo bm -j DROP

# After状态
echo "=== AFTER Rule 6 ===" >> ~/lab_log.txt
iptables -vL -n >> ~/lab_log.txt

# 测试
curl -I http://facebook.com  # 应该失败或超时
curl -I http://baidu.com  # 应该成功
```

### 规则7：允许出站SSH
```bash
# Before状态
echo "=== BEFORE Rule 7 ===" >> ~/lab_log.txt
iptables -vL -n >> ~/lab_log.txt

# 允许出站SSH连接
iptables -A OUTPUT -p tcp --dport 22 -j ACCEPT
iptables -A INPUT -p tcp --sport 22 -m state --state ESTABLISHED -j ACCEPT

# After状态
echo "=== AFTER Rule 7 ===" >> ~/lab_log.txt
iptables -vL -n >> ~/lab_log.txt

# 测试（如果有其他服务器）
# ssh user@another-server  # 应该成功
```

### 规则8：允许其他出站协议
```bash
# Before状态
echo "=== BEFORE Rule 8 ===" >> ~/lab_log.txt
iptables -vL -n >> ~/lab_log.txt

# 允许FTP
iptables -A OUTPUT -p tcp --dport 21 -j ACCEPT  # FTP控制
iptables -A OUTPUT -p tcp --dport 20 -j ACCEPT  # FTP数据
iptables -A INPUT -p tcp --sport 21 -m state --state ESTABLISHED -j ACCEPT
iptables -A INPUT -p tcp --sport 20 -m state --state ESTABLISHED -j ACCEPT

# 允许Telnet
iptables -A OUTPUT -p tcp --dport 23 -j ACCEPT
iptables -A INPUT -p tcp --sport 23 -m state --state ESTABLISHED -j ACCEPT

# 允许XMPP
iptables -A OUTPUT -p tcp --dport 5222 -j ACCEPT
iptables -A INPUT -p tcp --sport 5222 -m state --state ESTABLISHED -j ACCEPT

# After状态
echo "=== AFTER Rule 8 ===" >> ~/lab_log.txt
iptables -vL -n >> ~/lab_log.txt

# 测试
# telnet towel.blinkenlights.nl  # 如果可用
```

### 规则9：安装服务并允许入站访问
```bash
# 安装Apache Web服务器
sudo apt install apache2

# Before状态
echo "=== BEFORE Rule 9 ===" >> ~/lab_log.txt
iptables -vL -n >> ~/lab_log.txt

# 允许入站HTTP访问
iptables -A INPUT -p tcp --dport 80 -j ACCEPT

# 启动Apache服务
sudo systemctl start apache2
sudo systemctl enable apache2

# After状态
echo "=== AFTER Rule 9 ===" >> ~/lab_log.txt
iptables -vL -n >> ~/lab_log.txt

# 测试
curl -I http://localhost  # 本地测试
# 从主机测试虚拟机：curl http://虚拟机IP地址
# 或在虚拟机内测试：curl http://127.0.0.1
```

### 规则10：规则优先级测试
```bash
# Before状态
echo "=== BEFORE Rule 10 ===" >> ~/lab_log.txt
iptables -vL -n >> ~/lab_log.txt

# 添加冲突规则 - 先DROP后ACCEPT
iptables -A INPUT -p tcp --dport 8080 -j DROP
iptables -A INPUT -p tcp --dport 8080 -j ACCEPT

# 测试第一种情况
nc -l 8080 &  # 在后台启动监听
# 从另一个终端测试：telnet localhost 8080

# 清除规则并反向测试
iptables -D INPUT -p tcp --dport 8080 -j DROP
iptables -D INPUT -p tcp --dport 8080 -j ACCEPT

# 添加冲突规则 - 先ACCEPT后DROP
iptables -A INPUT -p tcp --dport 8080 -j ACCEPT
iptables -A INPUT -p tcp --dport 8080 -j DROP

# After状态
echo "=== AFTER Rule 10 ===" >> ~/lab_log.txt
iptables -vL -n >> ~/lab_log.txt

# 再次测试
# telnet localhost 8080  # 观察结果差异
```

## 高级功能探索（选择一项）

### 选项A：速率限制
```bash
# 限制SSH连接频率（防暴力破解）
iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --set --name SSH
iptables -A INPUT -p tcp --dport 22 -m state --state NEW -m recent --update --seconds 60 --hitcount 4 --name SSH -j DROP

# 限制ICMP速率
iptables -A INPUT -p icmp --icmp-type echo-request -m limit --limit 1/s --limit-burst 2 -j ACCEPT
iptables -A INPUT -p icmp --icmp-type echo-request -j DROP
```

### 选项B：TCP标志过滤
```bash
# 阻止TCP SYN flood攻击
iptables -A INPUT -p tcp --tcp-flags SYN,ACK,FIN,RST RST -m limit --limit 1/s -j ACCEPT

# 阻止无效的TCP标志组合
iptables -A INPUT -p tcp --tcp-flags ALL NONE -j DROP
iptables -A INPUT -p tcp --tcp-flags ALL ALL -j DROP
```

### 选项C：NAT设置（适用于虚拟机网络实验）
```bash
# 启用IP转发
echo 1 > /proc/sys/net/ipv4/ip_forward

# 查看虚拟机网络接口
ip addr show

# 设置SNAT（如果虚拟机有多个网络接口）
# 将eth0替换为实际的外网接口名称
iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE

# 设置端口转发（虚拟机内部端口映射）
iptables -t nat -A PREROUTING -p tcp --dport 8080 -j REDIRECT --to-port 80

# 虚拟机特定：设置主机到虚拟机的端口转发
# 这通常在虚拟机软件（如VirtualBox、VMware）中配置
```

## 实验完成后的清理

```bash
# 保存当前规则（如果需要）
iptables-save > ~/iptables_experiment.rules

# 恢复原始配置
iptables-restore < ~/iptables_backup.rules

# 或者完全清理（虚拟机环境相对安全）
iptables -P INPUT ACCEPT
iptables -P OUTPUT ACCEPT
iptables -P FORWARD ACCEPT
iptables -F
iptables -X

# 虚拟机特定：恢复到快照状态
# 可以直接在虚拟机软件中恢复到实验前的快照
```

## 测试命令参考

### 网络连接测试
```bash
# 基本连接测试
ping -c 3 8.8.8.8
curl -I http://www.baidu.com
wget --spider http://www.google.com

# 端口测试
nc -zv google.com 80
telnet google.com 443

# 查看网络状态
ss -tuln
netstat -tuln

# 虚拟机特定：测试主机与虚拟机连接
# 从主机ping虚拟机：ping 虚拟机IP
# 从虚拟机ping主机：ping 主机IP或网关IP
ip route show  # 查看路由表
```

### 日志查看
```bash
# 查看系统日志
tail -f /var/log/syslog | grep iptables

# 查看内核消息
dmesg | grep iptables
```

## 报告要求

对每个规则记录：
1. **Before状态**：规则实现前的iptables输出和连接测试结果
2. **精确命令**：使用的具体iptables命令
3. **After状态**：规则实现后的iptables输出和连接测试结果
4. **效果说明**：规则的实际影响和观察到的变化
5. **截图证据**：关键步骤的终端截图

记住：iptables规则是按顺序处理的，第一个匹配的规则决定数据包的命运！