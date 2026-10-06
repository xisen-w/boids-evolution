# 三项缺口补齐与验收结果

日期：2026-10-07。

后续按用户新指令完成了补齐后真实复验，见 [SMOKE_REVALIDATION_2026-10-07.md](SMOKE_REVALIDATION_2026-10-07.md)。本文保留补齐当时的源码、零新增调用和待审核状态，不冒充后续执行记录。

**结论：上一轮指出的机制分析、阶段 B 入口／预算、后期输入容量三项工程缺口已补齐，并完成代码回归、Docker 检查及真实旧产物复核。可以进入小实验配置审核；没有启动新付费实验。**

这不是宣称所有科学机制都已出现，也不是声称已真实跑过 8 agents × 12 轮。真实协作边不足和 alignment fallback 的边界继续保留，不能用人工测试用例代替研究证据。

## 1. 已补齐的内容

| 原问题 | 实际修改 | 验收结果 |
| --- | --- | --- |
| 实验 2–4 分析未接入 | 新增独立行为重复、可靠覆盖、逐轮覆盖、直接跨 agent 功能边消融、M_cross 上下界、任务深度及配对汇总；接入四组运行入口 | run-12 四组的实际工具已全部完成新增分析；失败／unknown／不可比较均保留 |
| 阶段 B 入口只认 smoke 参数 | 新增版本化阶段 B 配置；按配置使用 8 agents、12 轮、seed 2001、指定组序；调用数与费用按真实安排计算 | 384 次构建＋48 次 solver＝432；本地 432 次模拟调用的入口／账目测试通过；实际批准仍为 false |
| 16 KB 无法容纳后期目录 | 新阶段输入上限 32,768 bytes；solver 仅按统一规则压缩 prose，保留全部工具接口与任务；必要信息仍装不下则提前停止 | 四组 × 8 agents 的 88 工具历史输入全部通过，最大 23,572 bytes；96 工具 solver 目录覆盖 6 题 × 2 次，最大 28,911 bytes |

容量检查使用由真实元数据复制出的合成历史，是输入容量检查，不是新跑的 12 轮社会。旧 smoke 的 16 KB 配置不变，原始结果不覆盖。

代码入口：

- [analysis.py](../boidsnet/runner/analysis.py)：独立测量、分类、汇总及原始产物校验。
- [analysis_worker.py](../boidsnet/runner/analysis_worker.py)：运行时调用追踪与 importer-specific identity 消融，沿用现有 Docker／ACL／超时边界。
- [sac_pilot.py](../boidsnet/runner/sac_pilot.py)、[agentport_config.py](../boidsnet/runner/agentport_config.py)：版本化配置、动态调用／费用上界与分析集成。
- [utility.py](../boidsnet/runner/utility.py)、[exposure.py](../boidsnet/runner/exposure.py)：solver 目录容量检查，原格式优先，接口不截断。

## 2. 两轮验收实际做了什么

### 第一轮：实现与明确的正／负测试用例

- 验证正确与错误输出、共同报错不算行为重复、参数和 probe 分配固定、空分母为未定义、unknown 不补零。
- Docker 验证静态／相对／动态 import、函数别名以及只替换指定调用者；同一依赖被其他调用者使用时仍保留原功能。
- 手写完整分析 fixture 确认：真正 load-bearing 的边进入分子，dependency-only 模块不进入分母，逐轮可靠覆盖计算正确。它明确标为人工 fixture，不混入真实结果。
- 预算、权限、超时、错误分类、gate、参数化工具和原有四组流程完成回归；不通过放开非法调用或改模型答案让测试成功。

### 第二轮：原始证据与独立算术复查

- 48 个历史 builder prompt 仍能逐字重建；没有同轮可见性变化。
- 48 条真实归档 solver 回答重新执行，全部评分、gate 与冻结库保持一致。
- 新增分析执行 **2,112 条独立 probe 条件**。每条 intact 条件分别用普通 worker 和插桩 worker 执行，输出全部一致；这些 probe 不是 2,112 个独立社会样本。
- 从缓存的逐条输出独立重算可靠性、原始／冻结覆盖、行为可比较与重复分类、逐轮覆盖和开发分数，结果一致。
- 原始四组目录前后文件 hash 相同；冻结工具／依赖源码与原始库相同，ACL 也逐项一致。
- 历史累计账本再次完整核对：仍是 387 次请求、预留 19.1988448 元、累计上限 30 元、已关闭。本次新增真实模型调用 **0**。

### 测试计数与版本边界

| 测试组 | 结果 |
| --- | --- |
| 最终代码的针对性回归 | 156 项：142 通过、14 跳过；跳过的是显式 Docker 分组 |
| 最终代码的 Docker 分析／沙箱／参数化回归 | 33 项全部通过 |
| 三种四组离线集成流程 | 3 项全部通过；模型调用均为本地模拟 |

这些组有重叠，不将数字直接相加当成不同测试总数，也不宣称全仓或任意未来输入无 bug。三个较长集成进程在最后的分析输入校验补丁之前启动；最终补丁另由最终代码的完整分析 Docker fixture 及全部真实四组输入校验覆盖。

## 3. 二次审核中进一步收紧的地方

- **M_cross 不重复算传递边。** 只对被评工具自身的直接跨 agent 调用做分类，不把下游同一条边重复计给多个上游工具。该修正有专门回归测试。
- **插桩不能改变测量。** 普通 worker 是 intact 输出依据；如与插桩 worker 不同，追踪标 unknown，不悄悄接受改变后的行为。
- **原始／冻结库不能只比较源码。** 新增 ACL 一致性检查，避免冻结后执行权限变化时仍复用原始库测量。
- **普通非有限浮点输出不能让报告序列化丢结果。** 保存带标签的 NaN／Infinity，评分仍按原环境六位小数规范处理。
- **缺组、题目／尝试数不一致、重复社会、不同源码／环境／分析协议不能混成配对结果。** 汇总时拒绝，缺失不计零。

第一次离线分析中间目录 `archived_analysis` 在直接边口径修正时主动停止，保留为中间记录；完整结果来自 `archived_analysis_v2`，没有拼接部分社会。测量完成后仅又增加了 ACL 输入校验：用该最终函数复核了全部真实输入，不改写测量数值。

## 4. 新分析对现有 smoke 的判断

| 组别 | 原始库可靠操作数／22 | 冻结库可靠操作数／22 | 原有 dev solver 成功数／12 |
| --- | ---: | ---: | ---: |
| 000 | 7 | 7 | 0 |
| 100 | 11 | 11 | 4 |
| 011 | 10 | 10 | 2 |
| 111 | 10 | 10 | 0 |

这张表是旧模型产物的新增离线测量和旧评分整理，不是重新生成的实验，也不是四个独立重复的正式研究。

- 100 的覆盖和开发分数较高，但 111 没有优于 011。**不能把这批 smoke 总结成 separation 已有效**；当前科研信号仍然不明确，保留全部组和负结果。
- 可比较行为条件较少：000、100、011、111 分别为 12/78、3/69、6/72、6/72；这些可比较条件中的重复率均为 1。不能忽略可比较比例，单看重复率宣布“没有差异”。
- 所有冻结工具都没有有效完整任务 TARGET，M_cross 分母分别为 7、11、10、10，但它们缺少完整目标上的功能依赖判定。保留观察到的分子 0、未知数量与 `[0, 1]` 上下界，**不将其解释为真实协作效果已经证实为零**。
- 真实 alignment 仍是 fallback，真实构建没有跨 agent 导入；代码及人工 fixture 能处理非 fallback／有效依赖，不等于这些分支已在真实模型社会中出现。

实验复盘因此影响了本次实现：完成标记要求分析成功；缺失、不可比较与 unknown 都作为正式输出。没有为了支持 Boids 故事而补造工具依赖、换 seed 或改变 separation 阈值。

## 5. 下一步的待审核配置

- 每组 8 agents × 12 轮，四组各一个社会；seed 2001。
- 四组执行顺序：011 → 100 → 111 → 000。
- AgentPort `azure:DeepSeek-V4-Flash`，串行、无重试；同一 Mac＋固定 Docker 镜像。
- 60 道 dev 构建任务、每次菜单 8 道；固定 6 道 dev 题，每题 2 次 solver 尝试；不解封 test。
- **432 次请求，本地预留上限 60 元，单请求上限 0.15 元；完整最坏预留 59.513472 元。** 这是新提案，不是已批准预算、实际花费或网关账单。
- 必须用户确认新配置后再执行。旧 30 元修复批次继续关闭，不复用旧批准，不自动扩到正式主实验。

完整人类可读说明见 [STAGE_B_AND_ANALYSIS.md](STAGE_B_AND_ANALYSIS.md)。配置文件见 [agentport_flash_stage_b.json](../configs/agentport_flash_stage_b.json)。

## 6. 可复查交付物与源码

- 最终当前代码 SHA256：`869b7b314f6298332f840804cc9f6c228a4c37e2cdc53a503c24072d6266ee5b`。
- 真实工具离线测量代码 SHA256：`beab21b6f072ef66e3524e27e16b0111131fe6761184112704c509aa1d4f8280`；随后只加了上述 ACL 前置校验，最终校验回执记录了两版本，未覆盖测量 provenance。
- 历史真实 run-12 代码 SHA256：`efd54e575056d40b981163771f01ac7453ec09862bee03bc770df589c1ee6e40`，不冒称旧模型请求使用了新代码。
- 当前批准包：[proposed_launch_final](../review/stage_b_readiness_2026-10-07/proposed_launch_final/)，批准模板为 `PENDING_HUMAN_REVIEW / approved=false`；较早的 `proposed_launch` 因源码变化已失效，不删除、不复用。
- 真实旧工具分析：[archived_analysis_v2/paired_summary.json](../review/stage_b_readiness_2026-10-07/archived_analysis_v2/paired_summary.json)。
- 最终验收：[FINAL_VALIDATION.json](../review/stage_b_readiness_2026-10-07/FINAL_VALIDATION.json)、[FINAL_INDEPENDENT_AUDIT.json](../review/stage_b_readiness_2026-10-07/FINAL_INDEPENDENT_AUDIT.json)、[FINAL_CAPACITY_AUDIT.json](../review/stage_b_readiness_2026-10-07/FINAL_CAPACITY_AUDIT.json)、[FINAL_ARCHIVED_REPLAY.json](../review/stage_b_readiness_2026-10-07/FINAL_ARCHIVED_REPLAY.json)。

历史账目审计脚本原先额外要求“当前代码必须等于 run-12 代码”，升级后这一条件当然不再成立。最终独立审计保留了其全部金额／请求／哈希链断言，仅将该条件改为核对已知历史源码，同时单独记录当前源码；没有修改旧审计脚本、账本或批准记录。

本次没有新增付费请求，没有解封 test，没有修改旧模型输出或评分，没有公开上传原始研究产物，也没有推送 GitHub。
