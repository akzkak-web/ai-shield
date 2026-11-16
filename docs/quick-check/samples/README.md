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

**诚实性声明**：这不是真实 Ollama 实例的评估结果。真实 Ollama 集成
测试（`tests/integration/`）需要 Docker/Ollama 环境；本机当前没有可用
的容器运行时，相关用例尚未执行，详见项目交付说明。
