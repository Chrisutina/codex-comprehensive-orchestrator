# Codex Universal Orchestrator

这是一个面向 Codex 的综合性任务编排插件，不局限于写代码。它会根据用户目标选择合适的技能、文件工具、浏览器/电脑控制、外部资料、科学方法和受控的子模型协作，然后由主模型整合并验证最终结果。

## 支持的任务类型

- 编程、网页、调试、代码审计、自动生成测试；
- Word/Markdown/PDF 文档、PPT/PPTX 演示文稿、Excel/XLSX/CSV 表格和数据报告；
- 诗文赏析、哲学语录、文学分析、翻译和语境考证；
- 浏览器、桌面软件、文件操作、表单填写、截图和用户明确要求的游戏操作；
- 系统安全排查、木马/病毒线索分析、Defender 或其他可信扫描器结果整理；
- 仿真、科学计算、统计、计算生物学、生物信息学和文献分析；
- 网上查资料、时效信息核查、来源比较、事实核查和误导性论断分析；
- 混合任务，例如“查资料—做表格—生成 PPT—审计结论—写报告”。

## 核心分工

主模型负责：

- 理解用户真实目标；
- 识别风险和副作用；
- 规划关键路径；
- 选择工具和专业技能；
- 整合子模型结果；
- 最终检查和完整回答。

子模型或其他模型只处理边界清晰的辅助任务，例如资料搜集、独立审计、测试设计、版式检查、公式核对、来源交叉验证等。插件不会假设存在无限并发或某个固定模型供应商；当宿主不提供子模型工具时会自动顺序执行。

## 安全边界

- 系统扫描默认先读、不执行可疑文件、不擅自删除或隔离证据；
- 不把启发式检查冒充成完整杀毒结果；
- 删除、隔离、终止进程、安装软件、发布内容、发送消息、购买、部署、修改账号设置等操作需要明确范围，并在临近执行时确认；
- 不绕过游戏反作弊、DRM、权限控制、付费墙或账号保护；
- 科学和生物任务强调单位、参数、数据来源、可复现性、伦理和生物安全，不提供危险的病原体增强或规避防护内容；
- 网上研究会区分事实、观点、推测、指控、讽刺和无法验证的说法，并记录来源和日期。

## 目录

- `.codex-plugin/plugin.json`：插件清单；
- `skills/orchestrate/`：通用控制面和任务图编排；
- `skills/artifact-studio/`：文档、PPT、表格、PDF 和数据工件；
- `skills/computer-operation/`：浏览器、桌面软件和游戏操作；
- `skills/system-safety/`：防御性系统安全排查；
- `skills/simulation-biology/`：仿真、科学计算和生物信息学；
- `skills/web-research/`：资料查找、事实核查和误导信息分析；
- `skills/humanities/`：诗文、文学、哲学和语录赏析；
- `skills/code-audit/`：代码审计；
- `skills/test-engineering/`：测试工程；
- `skills/problem-solving/`：复杂问题分析；
- `scripts/universal_router.py`：跨领域路由器；
- `scripts/workspace_inventory.py`：只读工作区盘点；
- `scripts/task_router.py`：统一路由器的兼容入口；
- `scripts/test_command_detector.py`：测试命令建议器；`scripts/test_command_detector_unit.py`：测试命令建议器回归测试；
- `scripts/model_selector.py`：模型能力评估、缺口识别和切换/委托建议；
- `scripts/capability_prober.py`：供应商能力探测和自动发现（可选）；
- `skills/model-routing/`：智能模型抉择和多模型协作策略；
- `model_catalog.example.json`：用户可复制并自行配置的模型目录示例；
- `INSTALL.md`：安装、模型目录、API 密钥环境变量和清理说明；`install.py`/`install.ps1`/`install.sh`：跨平台自动安装与 Codex 注册。

## 安装

将整个插件目录复制到本地 Codex 插件目录，例如：

```text
C:\Users\<你的用户名>\.agents\plugins\codex-comprehensive-orchestrator
```

然后在本地 marketplace 中注册插件，重新加载 Codex。完整示例和开发更新方式见本目录中的 `INSTALL.md` 和 Plugin Creator 文档。

## 下载后自动配置

GitHub 不会也不应该在下载时静默执行代码；请运行一次下面的安装器完成安全的用户级配置。安装器会：

- 将插件复制到当前用户的 `~/plugins/codex-comprehensive-orchestrator`；
- 创建或合并个人 marketplace 配置；
- 创建一个所有外部模型默认禁用的 `model_catalog.json`；
- 如果检测到 `codex` CLI，自动注册 marketplace 并安装插件；
- 不创建、不读取、不上传 API 密钥。

Windows PowerShell：

```powershell
.\install.ps1
```

macOS/Linux：

```bash
python3 install.py
# 或
./install.sh
```

如需只复制文件而不修改 Codex 注册状态：

```text
python install.py --no-register
```

安装完成后请重新打开一个 Codex task/thread。模型供应商、API 地址和密钥仍需由用户通过授权的环境变量或宿主密钥管理器配置；安装器不会伪造或自动启用外部服务。

## 快速检查

```text
python scripts/universal_router.py "查找资料，核实误导言论并制作PPT" --json
python scripts/workspace_inventory.py . --json
python scripts/test_universal_router.py
python scripts/test_command_detector_unit.py
python scripts/model_selector.py "识别图片并制作PPT" --json
python scripts/capability_prober.py --catalog model_catalog.json --dry-run
```

## 智能模型路由

插件支持能力感知的模型选择和自动触发：

1. **能力推断**：从任务文本自动识别所需能力（vision、audio、video、artifact_generation 等）
2. **缺口检测**：对比当前模型能力，找出缺失项
3. **助手选择**：从已配置的模型中选择最小覆盖助手
4. **自动触发**：领域关键词自动触发对应能力检测，无需用户显式声明

示例：

```text
# 自动检测需要 vision + artifact_generation
python scripts/model_selector.py "识别图片中的文字并制作PPT" --catalog model_catalog.json --json

# 自动检测需要 audio + speech_recognition
python scripts/model_selector.py "把这段录音转成文字" --catalog model_catalog.json --json
```

运行 `capability_prober.py` 可自动探测已配置供应商的可用模型和能力：

```text
python scripts/capability_prober.py --catalog model_catalog.json --dry-run
```

这个插件是编排策略、领域技能和本地辅助脚本的组合，不是一个声称可以独立控制所有设备、无限调用模型或替代专业杀毒软件的万能程序。实际能力取决于当前 Codex 环境提供的工具、权限、连接器和用户授权。

## Intelligent model choice

The plugin now performs a capability-aware first pass before expensive or multimodal work. It can distinguish:

- the current model can complete the task (`use_current`);
- a configured specialist can cover a bounded missing capability (`delegate_missing_capability`);
- a configured model is materially better for quality or context (`switch_for_quality`);
- no configured provider exists, so the user must supply configuration (`request_user_configuration`).

The selector is deliberately offline and conservative. It does not call Qwen, OpenAI, or any other provider automatically, does not invent API access, and never emits API key values. Configure only models you actually own or are authorized to use, set `configured: true` only after setup, and keep keys in environment variables named by `api_key_env`. The primary model retains intent, safety, sensitive-data filtering, final choice, review, and synthesis.

Example with a user catalog:

```text
python scripts/model_selector.py "识别图片并制作PPT" --catalog model_catalog.json --json
```

If the result says `request_user_configuration`, the host should ask for the missing capability/provider rather than fabricate a result. Temporary API configuration must be removed after the task.

