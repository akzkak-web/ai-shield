# AI Shield 真实 Ollama 集成验证 — 验收报告

- 日期：2026-11-16（UTC 02:07–02:20）
- 执行环境：用户自有 Kali Linux VM（VMware Fusion，Apple Silicon）
- Kali：2026.3 Rolling，aarch64，内核 7.1.5+kali-arm64
- Docker：28.5.2（服务 active），containerd 2.1.9
- Ollama：容器 `ollama/ollama:latest`（镜像摘要 sha256:2ca7d8e6…），
  实测版本 0.40.4，仅绑定 127.0.0.1:11434
- 代码：`sprint/quick-check` 分支工作副本（未修改 main，未修改 Mac 原始仓库）

## 执行过程

1. VMware Fusion 快照 `AI Shield - Pre Integration Test` 创建成功（1 个快照）
2. `kail` 加入 docker 组（用户在 VM 控制台执行，密钥 SSH 验证通过）
3. rsync 传输 2.8 GB `ollama-arm64.tar` → `docker load` → `ollama/ollama:latest`
   （本地导入，无联网拉取）
4. rsync 工作副本 → `~/ai-shield`；创建 venv（Python 3.14.8）并安装
   `requirements.txt` + `requirements-dev.txt`
5. `docker run -d --name ai-shield-ollama -p 127.0.0.1:11434:11434`
6. `venv/bin/python -m pytest -m integration -q`
7. `quick-check 127.0.0.1 --ports 11434 …` 导出 JSON + PDF
8. 结果 rsync 回传 Mac 工作副本

## 结果统计

| 项目 | 结果 |
| --- | --- |
| 集成测试 | **4 passed / 0 failed / 0 skipped**（169 deselected，8.13s） |
| quick-check 退出码 | 0（fail gate PASS，附 partial coverage 提示） |
| 安全评级 | A，风险评分 0/100 |
| 检查覆盖率 | 6/6 执行：pass×3，unknown×3（auth_missing、model_access、resource_abuse） |
| 确认发现 | 0 |
| 服务识别 | Ollama 0.40.4 正确识别（127.0.0.1:11434） |

## 结果解释

容器未配置认证，但模型列表为空，因此「认证缺失」「模型访问」无法按
现有证据标准确认为漏洞，如实记为 unknown；「速率限制」未观测到，记为
unknown；CVE 检查确认 0.40.4 不在已知受影响版本范围内（pass）。
0 发现 + 3 项 unknown ⇒ 评级 A、覆盖 partial、退出码 0，CLI 明示
「no findings is NOT a security guarantee」，符合「保留 unknown 与 pass
区别、不虚报安全」的设计。

## 产物（已回传 Mac 工作副本）

`docs/quick-check/samples/real-ollama/`：

- `integration.log`
- `quickcheck_real.json`
- `quickcheck_real.pdf`
- `quickcheck_cli.log`
- `environment.txt`

## 仍未解决的问题

1. 3 项 unknown 需在客户带模型的实例上复核（本轮按约束未拉取模型）
2. Kali `daemon.json` 代理指向 127.0.0.1:7897，影响未来 `docker pull`，
   不影响本次 `docker load`
3. `vmrun snapshot` 命令本身在快照完成后未退出（约 5 分钟挂起），
   快照经 `listSnapshots` 与磁盘重做文件双重确认成功；属 Fusion 26.0.0
   的 vmrun 行为，不影响 VM
4. Kali 家目录现保留 2.8 GB `ollama-arm64.tar` 与测试容器（未删除任何数据）
