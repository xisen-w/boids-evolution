# 下一阶段小实验与独立机制分析

2026-10-07。本文是当前操作说明；早期官方 DeepSeek / legacy behavioral 入口与旧预算说明不再作为 SAC 小实验的启动依据。

本次补齐的是开发阶段入口和分析代码。**准备配置不等于批准执行，离线 fixture 不等于真实模型实验。** 旧 run-12 保持原状；新分析另存目录，新模型调用仍须先审核配置。

## 1. 待审核的小实验配置

- 配置文件：`configs/agentport_flash_stage_b.json`，版本 `sac-agentport-stage-b-v1`。
- 四组：000、100、011、111；执行顺序 **011 → 100 → 111 → 000**。
- 每组 **8 agents、12 个同步轮次、1 个空起点工具库**，seed 2001，环上邻居 2 个。
- 开发环境：固定 22 个 primitive、60 道 dev 任务，任务 seed 0；每 agent 每轮菜单 8 道。四组使用同样菜单安排。
- 评估：`dev-6311-d1`、`dev-6890-d1`、`dev-2407-d2`、`dev-5081-d2`、`dev-1528-d3`、`dev-6534-d3`；每题 2 次 solver 尝试、每次 8 个评分输入；不打开正式 test。
- 模型：AgentPort `azure:DeepSeek-V4-Flash`；base URL `https://agentport.world/v1`；允许返回 ID 为该 ID 或 `DeepSeek-V4-Flash`；按既有适配请求 `reasoning_effort=none`。
- Temperature 0.7；builder 输出 4,000 tokens、solver 1,500 tokens；不新增回复行数限制。
- Separation 阈值 0.3，alignment window 3，未为了增加触发改阈值或换题。
- 调用量：**384 builder＋48 solver＝432 次**。串行、无自动重试、无自动恢复；请求 deadline 90 秒、每个工具 probe 5 秒。
- 原始产物、冻结库和评分完成后，自动执行下方实验 2–4 分析；分析失败时不会报告整个阶段完成，也不会继续下一组付费请求。

### 输入容量与预算的变化

- 新阶段输入上限 **32,768 UTF-8 bytes**，旧 smoke 仍保留 16,000。Builder 仍对同一快照的四种规则渲染共同检查、同步压缩；不丢任务、工具成员或规则证据模块。
- Solver 优先使用完整原格式；不足时统一缩减描述／docstring 的 prose 部分，保留全部工具 ID、作者、执行签名、IMPLEMENTS、已声明 primitive 的调用参数和完整任务。不能容纳这些必需信息时停止，而不是偷偷丢工具。
- 当前本地记账参数保持输入 3.2、输出 8.4 元／百万 tokens。输入按实际 UTF-8 字节加 512 预留；不是精确 tokenizer，也不是已确认供应商账单。
- 新阶段建议本地熔断上限 **60 元**，单请求预留上限 **0.15 元**。432 次全部达到输入／输出上限时预留 **59.513472 元**；没有把未用输出额度退回再花。
- 旧计划的 35 元无法在当前路由、输入预留和输出上限下保证完成。这里调整的是待审核上限，不表示已花 60 元，也没有修改网关限额或旧修复批次的累计 30 元授权。
- 不增加模型、数据集、seeds、重试或防御性实验。用户未批准新配置前不能启动。

## 2. 实验 2–4 的实际计算

- **文字重复：**原始库的 label＋description，TF-IDF/cosine，所有不重复工具对的均值；少于两个工具或空词表时保留未定义状态。
- **行为重复：**无参数条件使用 40000–40007；同一声明 primitive 的三个参数 draw 分别使用 40000–40007、40008–40015、40016–40023。只有双方在同一条件的 8 张表上都返回合法表格才可比较，全部一致才重复；共同报错不算重复。
  - 固定统计单位为“无序工具对 × 共享参数条件”，同时给无参数、参数化、总体三套分子／分母及可比较比例；不将这些条件当独立 society 样本。
- **独立可靠覆盖：**每个 primitive 用原 sampler，`Random(45000 + crc32(name.encode('utf-8')) % 2000)` 连续抽三组参数；第 j 组在 `45000+4j ... 45003+4j` 上验证，全 12 次正确才覆盖。
  - 同时输出每工具、每 primitive 的通过率、正常运行率、未知声明，原始库与 solver 可见冻结库分开汇总，操作全集固定 22 个。
- **逐轮覆盖：**按创建轮次重建可靠能力并集；同轮工具都相对于轮初历史计算新增能力，避免把执行先后误当可见历史。不是每轮重新调用 solver。
- **功能依赖：**只对 solver 可见冻结工具及其依赖闭包分析。静态引用与受 ACL 约束的实际 execute 调用记录共同构成候选；对声明的有效 dev 目标使用固定 47000–47007。
  - 候选边限于被评工具自身直接调用的跨 agent 依赖；不会把依赖链更下游的同一条边重复归给每个上游工具。依赖闭包用于确保执行完整，不用于扩大 M_cross 分母。
  - Intact 使用原库；消融仅将指定 importer 对指定 dependency 的 execute 调用换为 identity。其他调用者仍得到真实依赖功能。
  - 所有 intact 分析 probe 也交普通、未插桩 worker 执行。若插桩输出不同，普通 worker 输出是测量依据，调用追踪标 unknown。
  - 非 execute 的跨工具 helper 调用、追踪缺失或无法确认替换命中均标 unknown；不把“追踪不到”当“没有依赖”。这不是任意 Python 数据／对象依赖的万能追踪器。
  - 分类：功能 load-bearing、未观察到作用、未使用、结构性、intact 已失败、unknown。为避免把崩溃当功能证据，消融结果含任何崩溃时保守归为结构性。
  - 每个 solver 可见工具最多进入 M_cross 分子一次；依赖闭包里仅供其他工具调用的模块不进入分母。无有效目标仍保留在分母并单列；给观察到的分数及 unknown 上下界，空库为未定义。
- **任务深度：**复用已经存下的 dev 逐题、逐次评分，核对 gate/verdict 后计算三个深度结果与配对差值；给“多步平均增益−单步增益”。四组的题目、尝试数、规模、分析版本与源码必须匹配。
- 保留逐 probe 输出与 reference，便于独立复查。非有限浮点输出保存为带 `__nonfinite_float__` 标记的 JSON 对象；评分先按原环境数值规范计算，不能用序列化变化改结果。

目前入口专用于开发阶段及已有 dev 产物。它不解封测试，也不冒充已经批准或完成正式主实验。每组一个社会的差值仅供诊断，不报告显著性或保证正效应。

## 3. 先准备，不调用模型

在仓库根目录、Docker Desktop 已运行时执行：

```sh
.venv/bin/python -m boidsnet.runner.mac_smoke prepare \
  --config configs/agentport_flash_stage_b.json \
  --out review/stage-b-review \
  --run-out runs/stage-b-approved
```

该命令只验证本地 Docker、生成 `config.json`、`resolved_config.json`、镜像回执及 **approved=false** 的批准模板，不读取 key、不创建模型客户端。目录必须全新。

审核包绑定完整配置、源码 hash、依赖声明、环境与 dev 任务 seal、机制分析协议、唯一运行 ID、绝对输出目录及预算。代码或配置变化会使旧批准失效。只有用户明确批准后才能产生批准文件；不要把模板的存在当批准。

## 4. 对现有四组 smoke 补做分析

```sh
BOIDS_SANDBOX=docker \
BOIDS_DOCKER_IMAGE=sha256:0e379b4303072d494085de56dbfc73924845f30daa1a91d0aaee19fb50f6cdf1 \
.venv/bin/python -m boidsnet.runner.analysis \
  --run smoke/agentport_repair_campaign_2026-10-06/run-12 \
  --out review/run12-independent-analysis
```

也可用 `--society <单个社会目录>` 替代 `--run`。输出必须位于原始目录之外，不能覆盖已有输出。原始文件和分析源码前后校验；已有模型响应、冻结选择和评分不改写。

输出包括每个工具的 probe 缓存、可靠验证、配对行为结果、声明目标与消融轨迹、社会分析、四组配对汇总及原始文件 hash。无目标、没有边、不可比较、错误与 unknown 都保留；不能只挑有利指标。

## 5. 停止与验收边界

- 预算超限前停止发送；超时、usage／返回模型异常、权限或基础设施错误仍熔断。普通错误模型答案继续记失败，不修原响应、不补采样。
- 分析异常保留 `FAILED.json`；不把缺失分析当零指标或阶段完成。
- 付费流程中的分析还启用 `stop_on_smoke_anomaly`：普通 worker 或插桩 worker 发现超时、权限／资源异常即停止，不再请求下一组；普通模型 Python 错误仍保留失败结果。独立归档分析默认仍可保留未知状态，未将其冒充通过。
- 原 smoke 的 paid 证据仍属于旧源码版本。新代码的人工集成验证、旧回答重放和旧工具分析必须分别标注；不能称已经真实运行过 8 agents × 12 轮。
- 不为得到正效果而改 threshold、选 seed 或人工给真实库补依赖。下一步是否运行，取决于离线验收和用户对完整新配置的批准。
