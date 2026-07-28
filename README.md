# 🛡️ AI Shield

**Local AI Security Scanner / 本地 AI 安全扫描工具**

[English](#english) | [中文](#中文)

---

## English

AI Shield is a one-click security scanner designed to audit locally deployed AI services (Ollama, vLLM, LM Studio, llama.cpp, etc.) for common security misconfigurations and vulnerabilities.

### Features

- 🔍 **Auto Discovery** — Detects AI services on common ports
- 🔓 **Auth Check** — Verifies if authentication is missing
- 🌐 **Network Exposure** — Checks if API is externally accessible
- 🐛 **CVE Matching** — Matches known CVEs for detected services
- 💉 **Prompt Injection** — Tests system prompt extraction
- 💧 **Data Leakage** — Tests for PII in model responses
- 📁 **File Read** — Tests local file access via API
- ⚡ **Rate Limiting** — Checks for resource abuse protection
- 🔗 **CORS Audit** — Validates cross-origin policy
- 🤖 **Model Access** — Checks unauthorized model listing

### Supported Services

| Service | Default Port |
|---------|-------------|
| Ollama | 11434 |
| vLLM | 8000 |
| llama.cpp / LocalAI | 8080 |
| LM Studio | 1234 |
| Open WebUI | 3000 |
| Text-Generation-WebUI | 7860 |

### Quick Start

#### One-Click Install

```bash
curl -sL https://raw.githubusercontent.com/USER/ai-shield/main/install.sh | bash
```

#### Web UI

```bash
ai-shield web
# Open http://127.0.0.1:8899
```

#### CLI Scan

```bash
ai-shield scan 127.0.0.1
ai-shield scan 192.168.1.100 --ports 11434,8000,8080
ai-shield scan 10.0.0.1 -o report.json
```

### Requirements

- Python 3.9+
- pip

### Development

```bash
git clone https://github.com/USER/ai-shield.git
cd ai-shield
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python ai-shield.py web
```

### Security Grading

| Grade | Risk Score | Meaning |
|-------|-----------|---------|
| A | 0-9 | Secure |
| B | 10-24 | Minor issues |
| C | 25-39 | Needs attention |
| D | 40-59 | Significant risks |
| F | 60+ | Critical vulnerabilities |

### License

MIT License

---

## 中文

AI Shield 是一款一键式安全扫描工具，专门用于检查本地部署的 AI 服务（Ollama、vLLM、LM Studio、llama.cpp 等）的常见安全配置问题和漏洞。

### 功能特性

- 🔍 **自动发现** — 检测常见端口上的 AI 服务
- 🔓 **认证检查** — 验证是否缺少身份认证
- 🌐 **网络暴露** — 检查 API 是否对外暴露
- 🐛 **漏洞匹配** — 匹配已知 CVE（Ollama/vLLM 等）
- 💉 **Prompt 注入** — 测试系统提示词是否可被提取
- 💧 **数据泄露** — 测试模型响应中是否包含 PII
- 📁 **文件读取** — 测试是否可通过 API 读取本地文件
- ⚡ **速率限制** — 检查是否有资源滥用防护
- 🔗 **CORS 审计** — 验证跨域策略配置
- 🤖 **模型访问** — 检查未授权用户是否可列出模型

### 支持的服务

| 服务 | 默认端口 |
|------|---------|
| Ollama | 11434 |
| vLLM | 8000 |
| llama.cpp / LocalAI | 8080 |
| LM Studio | 1234 |
| Open WebUI | 3000 |
| Text-Generation-WebUI | 7860 |

### 快速开始

#### 一键安装

```bash
curl -sL https://raw.githubusercontent.com/USER/ai-shield/main/install.sh | bash
```

#### Web 界面

```bash
ai-shield web
# 打开 http://127.0.0.1:8899
```

#### 命令行扫描

```bash
ai-shield scan 127.0.0.1
ai-shield scan 192.168.1.100 --ports 11434,8000,8080
ai-shield scan 10.0.0.1 -o report.json
```

### 环境要求

- Python 3.9+
- pip

### 开发模式

```bash
git clone https://github.com/USER/ai-shield.git
cd ai-shield
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python ai-shield.py web
```

### 安全评级

| 等级 | 风险分数 | 含义 |
|------|---------|------|
| A | 0-9 | 安全 |
| B | 10-24 | 轻微问题 |
| C | 25-39 | 需要关注 |
| D | 40-59 | 显著风险 |
| F | 60+ | 严重漏洞 |

### 许可证

MIT License
