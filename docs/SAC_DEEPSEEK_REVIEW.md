# Boids 小实验：代码审核与待批准配置

2026-10-06。当前状态：代码准备与离线软件验证；**没有启动真实模型实验**。

后续严格复查及修复见 [STRICT_REAUDIT_2026-10-06.md](STRICT_REAUDIT_2026-10-06.md)。下面的美元小实验配置不等同于新提出的 500 元完整研究方案；任何旧批准均因源码变化失效。HTTP 现在增加了真正的总时长 deadline：到期会关闭本地连接并终止本次运行，不自动重采样；服务端是否仍计费视为未知，保留费用预留。

> 2026-10-07 更新：本文保留初期官方 DeepSeek 路由的历史审核记录，不能作为当前启动配置。
> 当前使用 AgentPort，核心 smoke 已完成；新增机制分析和阶段 B 入口见
> [STAGE_B_AND_ANALYSIS.md](STAGE_B_AND_ANALYSIS.md)。其中“尚未实现”的历史段落按当时状态阅读；
> 新阶段仍须新配置批准，不会沿用已关闭的 smoke 修复授权。

## 1. 审核依据与范围

- GitHub：`xisen-w/boids-evolution`。
- 本轮基线：`claude/codebase-setup-201ak0`，commit `60097b0de92fb1a9f8027ea6d62b0cba04365f51`；这是本轮查询到的最新远端分支，不是旧 `main`。
- 工作分支：`codex/sac-deepseek-small-pilot`。没有修改原有脏工作区；修复与两轮复核见 [BUGFIX_AUDIT.md](BUGFIX_AUDIT.md)。
- 科学依据：用户的 continuation draft，以及 2026-10-05 中英实验计划。新代码落实后者明确写出的 S/A/C 操作定义，不声称是伙伴未公开补丁的原样复现。
- 本轮目标：先准备四组的小规模开发集检查，不启动正式实验，不以试跑挑选有利结果。

## 2. 原代码的问题与本轮处理

| 问题 | 本轮处理 |
|---|---|
| 原 runner 只有 E/L0/R0/IM 等旧组；不是三位 S/A/C 设计 | 新增独立 SAC 路径，保留旧组，不把 L0 直接改名为 100 |
| 旧 separation 按行为 hash 比较自己与邻居 | 新 S 按邻居工具名称和描述计算 TF-IDF/cosine，阈值 0.3，最多两工具 |
| 缺少 A 和 C 的独立开关 | A 使用近 3 轮邻居工具的开发通过状态、TCI、静态引用数；C 使用上一轮声明活动统计 |
| Neutral 可能被误当成不共享信息 | 四组保留相同目录、访问权限、证据选择规则；只切换主动/中性指导句 |
| DeepSeek 默认思考模式与预期采样不明确 | 请求显式发送 `thinking={type:disabled}`，固定 temperature=0.7；记录返回模型、结束原因和 usage |
| 旧命令默认查 OPENAI_API_KEY | 新入口只接受 `BOIDS_PARTNER_API_KEY`，不读取 .env，不回退到其他变量 |
| 原 transport 默认最多 6 次尝试，易增加小试跑费用 | 新入口每次调用最多 2 次 HTTP 尝试，总请求最多 120；每次发送前预留成本 |
| 开发与最终测试 coverage 输入在同一 seed 区间 | 测试 coverage 移到 [50000,60000)，开发侧 [30000,40000) 不变；任务说明不变 |
| Solver gate 可放过默认参数/类型注解里的额外逻辑 | 禁止默认参数、注解、重绑工具名、提前 return 等绕过 |
| 全部生成无法解析时，空库缺少 index/ACL 文件 | 初始化空库也写入完整空索引，可正常冻结为空库 |
| 同批探针共享模块和标准库的可变状态 | 每个探针从尚未加载生成代码的 driver 独立 fork，固定 random.seed(0) 和进程启动时的 PYTHONHASHSEED=0 |
| 缺少沙箱依赖时异常发生在捕获范围外 | 失败后识别为 hook-only；真实模型路径仍拒绝运行，不降低隔离要求 |
| 原 solver 只能完整评估 60 题，不适合极小检查 | 新增仅开发集可用的显式题目子集；测试集不允许只挑部分题 |

相同证据是指**相同历史快照输入下**，四组采用相同的选择规则与内容；真实运行后，各组自己积累的历史当然可能不同。不会把一个组的工具或反馈搬到另一个组。

TCI 仍是复杂度代理，不是质量分数。只有通过开发目标才标记 `dev_pass=true`；无通过者的 A 样例明确标记 fallback。Adoption 只是不同静态 importer 的数量，不当成成功协作。

## 3. 请审核的小实验配置

- **目的：**确认真实 DeepSeek 调用、四组 prompt、工具生成、隔离执行、冻结工具库和 solver 评估能够串起来；不用于声称 Boids 优于 baseline。
- **数据：**mechenv 的固定 60 道开发题，任务 seed=0，单步/两步/三步各 20 题；agent 每轮看到其中 8 题。
- **实验组：**`000`、`100`、`011`、`111`。数字按 S/A/C 排列；实际执行顺序固定为 `000 → 111 → 100 → 011`。
- **规模：**每组 4 个 agent，固定环形、每人两位邻居，运行 3 轮；种子 1001，每组仅一次独立运行。共 4 个工具库。
- **初始状态：**空库；每人每轮一次生成机会；新工具下一轮才可见；失败消耗机会，不额外修复生成。
- **模型：**builder 和 solver 都用官方 `deepseek-flash`；base URL=`https://api.deepseek.com`；关闭 thinking；temperature=0.7；不显式发送 top-p（官方非思考模式固定为 1）。
- **输出上限：**builder 4,000 tokens，solver 1,500 tokens；每个请求的 system+user 总 UTF-8 长度最多 16,000 bytes。这是保守的字节上限，不冒充精确的 16,000-token tokenizer 限制。
- **输入缩减：**在相同快照下同时检查四种 prompt，先同步减少 S/A 的代码摘录，再缩短公共目录说明；不删除任务或某个证据模块。仍超限就停下，不静默截断。
- **S/A/C：**S 阈值 0.3、最多两样例；A 窗口 3 轮，开发通过优先、TCI 排序，可加静态引用最多者；C 仅统计上一轮。
- **工具执行：**每条探针 5 秒超时；每题 8 张表；每条 probe 独立进程状态。结果行序、列和值均需匹配，浮点保留 6 位比较。driver/挂载/结果传输错误中止运行，不当成任务失败。真实运行仍必须通过 Linux OS 隔离检测。
- **冻结：**共同的开发侧筛选、行为去重和参数化 primitive 恢复规则；保留构建时 ACL 的传递闭包以支持延迟导入，但 dependency-only 不列给 solver，也不把额外保留的文件计成有效复用。
- **Solver：**从完整固定开发集的每个深度按原始顺序取前 2 题，共 6 题，每题独立尝试 2 次；只能串联已有工具。精确题目 ID 写进 resolved_config.json。
- **调用数：**生成 `4×4×3=48` 次；solver `4×6×2=48` 次；正常合计 **96 次**。HTTP 总上限 120，包括重试，不是 120 次额外生成。SDK 重试和自动重定向均关闭，避免单次预算登记产生额外 HTTP 请求。
- **失败处理：**网络/429/408/409/5xx 最多重试一次，每次请求超时 180 秒；不重试鉴权错误，不因解析失败重采样。不完整运行单独标记，不计作效果为零。
- **费用控制：**按当前官方高峰未缓存输入 $0.30/M、输出 $1.20/M 做保守预留，累计预留上限 **$2**。缓存折扣不用于放宽预算；超时请求不退还预留。金额是本地保守控制，不是服务商账单保证；记录实际 reported usage 和未获 response 的请求数。
- **凭据：**只允许伙伴通过运行环境提供 `BOIDS_PARTNER_API_KEY`。这里不放 key，不使用用户已有 key。
- **不做：**不解封测试题，不扩大独立重复，不自动开启下一阶段，不报告显著性或主实验结论。

小规模意味着 S 的相似样例、有效工具复用等可能很稀少。流程完成不等于机制得到验证；若某条机制没有机会触发，要先读日志并重新请用户审核后续配置。

## 4. 如何准备与启动

运行环境建议 Python 3.11（本次离线测试环境见验收记录），安装 `requirements.txt`。真实运行必须在通过现有 OS 隔离检测的 Linux 主机，不能通过设置 hook-only 绕过。

### 只准备：现在允许

```bash
python -m boidsnet.runner.sac_pilot \
  --config configs/deepseek_flash_small.json \
  --out review/deepseek-small \
  --run-out runs/deepseek-small-approved
```

输出 resolved_config.json 和 approval.template.json；后者默认 `approved=false`。配置绑定唯一 run ID 和完整目标目录。应在计划实际运行的 Linux 工作目录准备；跨主机路径不同必须重新准备和审核。此命令不创建模型客户端、不读取凭据、不执行模型生成的代码。

### 启动：必须先取得用户明确同意

1. 让用户审核上面的完整配置，以及准备文件的配置/代码指纹。
2. 获批后，把 approval.template.json 另存为 approval.json，填入真实审核者，设 `status=APPROVED`、`approved=true`。未经实际确认不得填写。
3. 由伙伴在 Linux 运行环境注入自己的 key。不要把 key 放进命令行历史、代码、JSON 或聊天。
4. 在审核时指定的目录启动；改代码、配置或运行目录会导致旧批准失效。批准单次使用，启动失败后也不能重用；与运行目录同级的 `.consumed` 标记必须保留。不能覆盖已有结果。

```bash
python -m boidsnet.runner.sac_pilot \
  --config configs/deepseek_flash_small.json \
  --review review/deepseek-small/resolved_config.json \
  --approval review/deepseek-small/approval.json \
  --out runs/deepseek-small-approved \
  --execute --allow-spend
```

批准文件是防误启动的流程门槛，不是身份认证或密码学签名；它不替代人的实际授权。

## 5. 输出与证据边界

- 每组：manifest、完整 builder prompt/response、rounds.jsonl、逐轮库快照、原始工具库、冻结记录、开发 solver gate/cost 日志。
- 总体：请求 ledger、成功收到响应的 usage、未知响应请求、共享开发诊断汇总；失败写入只含错误类型与 HTTP 状态的 FAILED.json，不写服务商异常原文。
- 开发 solver 的公开日志继续隐藏逐次结果；另在 `utility_dev/private_audit/` 保留完整 prompt、response、glue、imports、逐次 verdict、token usage、参数和 probe seeds，目录权限 0700、文件权限 0600。请求/响应到达时即落盘，中途失败仍保留已收到的证据。此目录不提供给生成工具或 agent，但运行所有者可审计、可解盲，因此不声称严格双盲。API 费用记录在总请求 ledger 中。
- 初次小检查之后，需要先评估格式、沙箱、工具调用和机制触发是否正常。任何真实 API 请求，包括最小接口验证，都仍须获用户批准。

## 6. 尚不能声称“整篇 paper 实验已经准备完”

- 实验 1 的四组构建和极小开发诊断路径已补齐，真实 DeepSeek 与 Linux OS 隔离下的端到端运行尚未验证。
- 原有正式批处理仍是旧行为组协议，**不能直接用它跑新的 SAC 大实验**。本轮入口有明确的规模上限。
- 实验 2 的独立行为重复/可靠 primitive 覆盖汇总，实验 3 的 importer-specific edge ablation 与 M_cross，实验 4 的统一统计表，还需要专门分析实现和离线验收。本轮保存了所需源码、作者、依赖、逐轮快照及 probe 元信息，但不把静态 import rate 充当 M_cross。
- 新测试 coverage 区间改变了 test seal：新候选 seal 是 `c9f634ae53c8f62694aed012f83520b53541175462552afdac5d1e40c93b7c0d`。旧 `25634f77…` 结果仍属于旧环境；不能混池，也不能声称新 seal 已在房间共同注册。
- 1 个种子只用于工程检查，不足以判断效果、稳定性或显著性。是否追加试跑、何时正式冻结，均另行审核。

## 7. 官方模型依据

- [DeepSeek models and pricing](https://api-docs.deepseek.com/quick_start/pricing/)：本轮核实时官方 API 名称为 `deepseek-flash`，对应 V4.1 Flash；不使用旧别名来暗示固定历史版本。
- [Thinking mode](https://api-docs.deepseek.com/guides/thinking_mode/)：思考默认开启，因此本配置显式关闭；不依赖服务端默认模式。
- [Chat completion API](https://api-docs.deepseek.com/api/create-chat-completion/)：请求格式、usage 和采样参数。

服务端模型别名可能更新，manifest 与每次响应记录实际返回的 model；这不是不可变模型权重的证明。

## 8. 初次准备验收记录（已被后续严格审查取代）

下面是修复前的历史测试记录，并非当前版本的充分验收结论。严格审查随后发现 11 项问题；当前修复和两轮复核以 [BUGFIX_AUDIT.md](BUGFIX_AUDIT.md) 为准。先前生成的审核文件因代码变化已经失效，不得启动。

- 完整测试套件：`Ran 105 tests in 316.552s`，`OK (skipped=3)`。
- 新增 SAC/DeepSeek 专项：23 个测试通过，包括四组共享证据、S 文字选择、A 回退/引用数、C 时间窗口、同步 ACL、空库、glue 绕过、凭据入口、批准指纹、预算与真实 SDK 的内存模拟传输。
- 跳过范围：2 个历史审计绘图测试缺少可选 matplotlib；1 组 OS 沙箱篡改测试因本机不支持 Linux 命名空间而跳过。没有把跳过项目算作已通过的安全验证。
- `compileall`、`git diff --check`、`pip check` 均通过。
- 环境：macOS/Darwin，Python 3.9.13；OpenAI SDK 1.51.0、httpx 0.27.2、scikit-learn 1.5.2、NumPy 2.0.2、SciPy 1.13.1；依赖装在此副本的独立 `.venv`，未改系统 Python。
- 测试使用人工 fixture、旧仓库自带的 stub 单测和模拟 HTTP 传输；主测试进程拦截 socket 网络连接。没有调用 DeepSeek 或任何实验模型 API，没有使用真实 API key。
- 首轮回归的唯一剩余失败是旧单测硬编码了旧 test seal；改为检查新版本常量后，完整重跑通过。环境版本变化已明确记录，不沿用旧 seal 冒充同一实验。
- 初次待审核文件生成时与当时源代码及 requirements 指纹一致；现已失效。`approval.template.json` 仍为 `approved=false` / `PENDING_HUMAN_REVIEW`。
- 这些结果只验证软件行为，不构成真实 DeepSeek 端到端验证、Linux OS 隔离验证或 Boids 效果证据。
