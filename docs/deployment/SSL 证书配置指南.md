# SSL 证书配置指南

**服务器信息：**
- 内网 IP：172.28.10.14
- 域名：aius.xin / www.aius.xin
- 系统：Alibaba Cloud Linux 3

---

## ⚠️ 重要提示

由于服务器位于内网（172.28.x.x），需要先确认：

1. **公网 IP：** 服务器是否有公网 IP 或 NAT 映射？
2. **DNS 解析：** 域名是否已解析到正确的公网 IP？
3. **80 端口开放：** 公网是否能访问服务器的 80 端口？

Let's Encrypt 验证需要公网可访问 80 端口。

---

## 方案 A：Let's Encrypt 免费证书（推荐）

### 前提条件
- 域名已解析到服务器公网 IP
- 80 端口公网可访问

### 步骤

**1. 验证 DNS 解析**
```bash
# 在本地执行
ping aius.xin
# 应该返回服务器公网 IP
```

**2. 申请证书**
```bash
certbot --nginx -d aius.xin -d www.aius.xin
```

**3. 按提示操作**
- 输入邮箱地址
- 同意服务条款
- 选择是否重定向到 HTTPS

**4. 验证自动续期**
```bash
certbot renew --dry-run
```

**5. 配置定时任务（已自动配置）**
```bash
# 查看定时任务
crontab -l | grep certbot
```

---

## 方案 B：阿里云免费 SSL 证书

### 适用场景
- 服务器无公网 IP
- 80 端口无法公网访问

### 步骤

**1. 登录阿里云控制台**
访问：https://ssl.console.aliyun.com/

**2. 申请免费证书**
- 选择「购买证书」→「免费证书」
- 填写域名：aius.xin
- 完成域名验证（DNS 验证）

**3. 下载证书**
- 证书类型：Nginx
- 下载后得到两个文件：
  - `aius.xin.crt`（公钥）
  - `aius.xin.key`（私钥）

**4. 上传到服务器**
```bash
# 创建目录
mkdir -p /etc/nginx/ssl

# 上传证书文件（使用 scp 或直接粘贴）
# /etc/nginx/ssl/aius.xin.crt
# /etc/nginx/ssl/aius.xin.key
```

**5. 更新 Nginx 配置**
编辑 `/etc/nginx/conf.d/aius.conf`，启用 HTTPS 配置块。

---

## 方案 C：自签名证书（仅测试）

### 适用场景
- 仅内部测试使用
- 浏览器会显示安全警告

### 步骤

**1. 生成自签名证书**
```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout /etc/nginx/ssl/aius.xin.key \
  -out /etc/nginx/ssl/aius.xin.crt \
  -subj "/C=CN/ST=Zhejiang/L=Huzhou/O=AIMED/CN=aius.xin"
```

**2. 配置 Nginx**
同上，启用 HTTPS 配置块。

---

## Nginx HTTPS 配置模板

```nginx
server {
    listen 443 ssl http2;
    server_name aius.xin www.aius.xin;
    
    # SSL 证书路径
    ssl_certificate /etc/nginx/ssl/aius.xin.crt;
    ssl_certificate_key /etc/nginx/ssl/aius.xin.key;
    
    # SSL 优化配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384';
    ssl_prefer_server_ciphers on;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # 安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    
    # 官网静态文件
    location / {
        root /root/.openclaw/workspace/static;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
    
    # API 代理
    location /api/ {
        proxy_pass http://127.0.0.1:18790;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # 静态资源缓存
    location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name aius.xin www.aius.xin;
    return 301 https://$server_name$request_uri;
}
```

---

## 验证配置

**1. 测试 Nginx 配置**
```bash
/usr/sbin/nginx -t
```

**2. 重载 Nginx**
```bash
/usr/sbin/nginx -s reload
```

**3. 测试 HTTPS 访问**
```bash
curl -I https://aius.xin
```

**4. 在线检查**
访问：https://www.ssllabs.com/ssltest/

---

## 常见问题

### 1. 证书申请失败
**错误：** `Failed authorization procedure`
**原因：** 80 端口无法公网访问
**解决：** 使用方案 B（阿里云证书）或 DNS 验证方式

### 2. 浏览器显示不安全
**原因：** 自签名证书或证书过期
**解决：** 使用正规 CA 颁发的证书

### 3. 混合内容警告
**原因：** HTTPS 页面加载了 HTTP 资源
**解决：** 确保所有资源使用相对路径或 HTTPS

---

## 证书续期

### Let's Encrypt 自动续期
```bash
# 手动测试续期
certbot renew --dry-run

# 正式续期
certbot renew

# 续期后重载 Nginx
certbot renew --deploy-hook "/usr/sbin/nginx -s reload"
```

### 阿里云证书手动续期
- 每年重新申请一次
- 下载新证书并上传
- 重载 Nginx

---

**下一步：** 请确认服务器是否有公网 IP，然后选择合适的证书方案。
