# 示例报告说明

本目录内的 `sample_report.json` 与 `sample_report.pdf` 由
`scripts/mock_ollama.py`（仅监听 127.0.0.1 的模拟 Ollama 服务）在本机
隔离测试环境中生成，用于演示完整输出。

生成命令：

```bash
python3 scripts/mock_ollama.py --port 18099 &
python3 ai-shield.py quick-check 127.0.0.1 --ports 18099 \
  --customer "示例客户有限公司" \
  --engagement-id QC-2026-DEMO-001 \
  --authorized-scope "127.0.0.1:18099 本地隔离演示环境" \
  -o docs/quick-check/samples/sample_report.json
```

PDF 由同一 JSON 结果生成。

**诚实性声明**：以上 `sample_report.*` 由模拟 Ollama 生成，仅用于演示。

## 真实 Ollama 集成验证

`real-ollama/` 目录保存了在用户自有 Kali VM（172.16.199.128，隔离环境）
上对**真实 Ollama 0.40.4 容器**执行的结果：

- `integration.log`：`pytest -m integration` → **4 passed, 0 failed, 0 skipped**
- `quickcheck_real.json` / `quickcheck_real.pdf`：真实 quick-check
  输出（评级 A、风险 0、覆盖率 partial、3 项 unknown、退出码 0）
- `quickcheck_cli.log`：CLI 完整输出
- `environment.txt`：验证环境信息（系统、Docker、镜像、容器、统计）

真实容器仅绑定 127.0.0.1:11434，未拉取模型、未做模型推理、未暴露公网。
