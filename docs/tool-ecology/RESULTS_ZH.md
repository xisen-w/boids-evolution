# 工具生态的分工实验：持续记录

日期：2026-10-09。核心仓库 xisen-w/boids-evolution，PR #2。当前结果是探索性机制实验，不是外部 benchmark 排行榜，也不承接旧 SAC 的 confirmatory freeze。

**测量更正：v0.3 漏计了直接 re-export 的邻居函数；中性小实验实际为 72 个正确跨作者请求，而非 0。** 错误计数还进入了部分 agent 已读取的私人反馈。旧主批次因此主动中止，保留两个已完成社会和一个部分完成的独立社会；修复后另启干净版本，不拼接结果。24 份工程发布已用修复后的 grader 重放，服务成绩全部不变，中性组新增的六条入口委托边也全部有非崩溃干预证据。下表是旧反馈条件下的修正后观察，不能替代新版本的条件比较。

## 目前实际看到了什么

完成一轮 GPT-6-Luna 小规模检查：4 个同等机会、无指定角色的 agent，3 轮，局部中性与局部 Boids。两组都面对六类持续的数据服务需求，可以自行选择建造、维护、复用哪些能力。工具使用原生 Python API；统一服务 adapter 只是让主机能独立验证它。

| 条件 | 有效发布 | 同时通过全部六类的发布 | 最终群体覆盖 | 修正后的正确跨作者请求 | 持续单类贡献 |
|---|---:|---:|---:|---:|---:|
| 局部中性 | 12 | 9 | 6/6 | 72 | 0 |
| 局部 Boids | 12 | 5 | 6/6 | 36 | 0 |

**发现了功能性采用，但还没有发现互补分工。** Boids 的 a00 第三轮把邻居 a01 第二轮的一整套实现包装成自己的六个服务接口。六条跨作者函数边各有独立的“不崩溃但丢失正确性”干预证据。36 是一个发布在六类、每类六个案例上的正确请求数，不能算成 36 个独立协作事件或社会样本。

中性组 a03 第二、三轮直接导出了 a02 第一轮的六个服务，是两个发布的 72 个正确请求；六条入口委托边均有干预证据。这里归因的是实际执行的服务提供者，不是包装作者亲自编写或理解了它。原始漏计表、修正记录和全部尝试分开保留。

[归因修复与重放](../../studies/tool_ecology/evidence/v03/engineering-01/entry-attribution/summary.json)

两组最后每个作者的累计已验证能力都覆盖六类，作者能力集合的 Jaccard 都为 1.0，重复作者—能力配对都达到 18（4×6−6）。这次采用更像通才实现的复用；没有证据证明清洗、统计、时间处理等能力被不同作者持续、互补地承担。

这里的累计能力首先指该作者历次发布**能提供的服务**，可能包含其他作者的依赖，不能直接解释成独立专长。冻结后又把全部 24 份发布放到同一个新 DEV 面板验证，并沿声明依赖剔除所有直接、间接需要其他作者的发布。两组仍各有作者仅凭自己的历史包覆盖全部六类，群体相对最佳自足作者的覆盖增量都是 0。逐一移除某作者及所有依赖它的发布，群体覆盖也都没有下降。这是已有工具图的结构诊断，未模拟移除后 agent 的适应。

[共同新面板验证](../../studies/tool_ecology/evidence/v03/engineering-01/fresh-panel/summary.json) · [依赖来源诊断](../../studies/tool_ecology/evidence/v03/engineering-01/fresh-panel/dependency-provenance-addendum.json)

## 我们具体测量什么

六类任务包括清洗、收入列生成、分组收入汇总、按月份/地区汇总、收入与地区目标比值、收入滚动均值。后四类依赖上游新生成的列，不能把两个互不相关的操作拼接后称为组合。

每轮所有 agent 得到相同机会和服务契约，自主决定贡献。主机在会话结束后，用六个新生成的 DEV 案例验证每个声明的服务，涵盖混合缺失、全缺失、空表、未知/零目标、缺失价格和变化参数。模型看不到这些私有输入或参考实现；下一轮只得到聚合能力反馈。这里的“验证”是通过这一有限案例面板，不是形式化正确性证明。

分别记录：单个请求是否正确；某类服务是否六个案例全过；正确请求是否实际调用其他作者；同一作者是否连续至少三轮发布恰好一类完整通过的能力；累计作者能力是否重叠。持续单类贡献不是专长排名，也不代表作者以前没有其他能力。

局部 Boids 与中性组有相同拓扑、可见信息、服务反馈、模型和预算上限；区别是 S/A/C 的方向性提示。这是 prompt 层面的局部规则，不是原始 Boids 连续位置/速度方程。独立条件只看自己的历史，结束后合库。每轮先固定全部视图，之后才运行和发布，禁止同轮泄漏。

调用记录覆盖普通 Python 函数、实例/静态/类方法和 property。不是完整的 native、反射、生成器调用图；因此零调用不等于完全不存在阅读或复制带来的信息影响。

## 结果是否可信

- 24 份相同发布去掉调用追踪后重新执行，全部服务成绩一致。原结果没有重写。
- 六条符合条件的实际跨作者边全部完成返回值干预；均有正确请求在无崩溃情况下丢失正确性。原始分数与诊断分开保存。
- 修复后 48 项原生工具和分析测试通过，包含真实 Docker、并发快照隔离、非法发布、输出合同、输入不变性、class 方法、直接/跨层导出、入口干预及自有历史别名。新增冻结后分析测试覆盖依赖连锁移除、通才冗余，以及不能把邻居包装误算为自足能力。旧 runner 的 Linux DEV CI 已通过。
- 新 Linux CI 暴露了一个权限 bug：删除 Docker capabilities 后，容器 uid0 不能写主机 uid1001 的目录。已在 Linux named volume 重现，改为使用主机数字 uid/gid；修复后的原生工具 Linux CI 已通过（1m15s / 1m28s），结果单独记录。此前 Mac 工程实验可正常写回，输出保留不变。

## 一项具体失败为什么发生

Boids 首轮 a00_r01 把地区名标准化放进公共 `_base`，但 revenue/window 的服务合同要求保留原地区值。这两个服务各只通过 1/6。单独诊断副本只把标准化限制在适用的四类服务中，两个服务都变为 6/6；其他四类保持 6/6。它说明 helper 的适用范围会污染组合结果，不证明 Boids 指令导致了这份程序的错误。第一次主机补丁的条件表达式优先级写错，未改变行为；该尝试和修正后的诊断都保留，原实验分数不改。

[独立诊断](../../studies/tool_ecology/evidence/v03/engineering-01/helper-scope-diagnosis.json) · [源代码差异](../../studies/tool_ecology/evidence/v03/engineering-01/helper-scope.diff)

进一步逐项比较全部失败输出：工程 Boids 组 63 个失败案例中，51 个只在 `region` 列不同；中性组 25 个失败全部只在该列不同。其余 Boids 失败包括列值或输出行数差异。列差异是描述性证据，不能自动推断每个程序都有相同原因，也不能据此断言 Boids 导致错误。

[失败输出字段审计](../../studies/tool_ecology/evidence/v03/engineering-01/output-differences.json)

## 实际成本和完整证据

本轮 107 次实际 Luna 请求：中性 54，Boids 53。输入 436,237 tokens，输出 42,462，缓存输入 304,487；API 错误 0。没有核实货币单价，所以不把 runtime 的 cost=0 当作免费。

- [修正后的机器结果](../../studies/tool_ecology/evidence/v03/engineering-01/entry-attribution/corrected-results.csv)
- [原始漏计表，保留审计](../../studies/tool_ecology/evidence/v03/engineering-01/results.csv)
- [干预与未追踪重放](../../studies/tool_ecology/evidence/v03/engineering-01/diagnostics.json)
- [修正后的轨迹图](../../studies/tool_ecology/evidence/v03/engineering-01/entry-attribution/figures/ecology-trajectories.svg)
- [中性组实际工具流向](../../studies/tool_ecology/evidence/v03/engineering-01/entry-attribution/execution-graphs/seed-9001/local-neutral/execution-graph.svg)
- [Boids 组实际工具流向](../../studies/tool_ecology/evidence/v03/engineering-01/entry-attribution/execution-graphs/seed-9001/local-boids/execution-graph.svg)
- [完整固定协议](EXPERIMENT_2026-10-09.md)
- [执行记录及失败](LEDGER.md)
- [修正版本固定协议](EXPERIMENT_V031.md)

完整 API 响应、轨迹和私有工作目录保存在本地主机 studies/tool_ecology/runs/demand-engineering-01；GitHub 发布清理后的工具、结果、快照收据和图，不发布凭据或完整 API 对话。

## 接下来的固定批次

配置为 8 agent × 6 轮，种子 71、108、2026，局部中性、局部 Boids、独立三种条件，总计九个社会。旧批次因测量/反馈 bug 已中止，不能称为完成九社会的实验。修复后的 v0.3.1 已从干净提交 `376966b`、全新工作目录 `demand-batch-02` 启动；每 agent 每轮最多六次模型调用，最多四个 agent 并发，整批最多 2,592 次请求。48 项本地测试、两次原生工具 Linux CI 和原核心 Linux DEV CI 均通过。

重点检验这次功能性采用是否重复出现，以及采用之后是否真的减少重复建造、形成持续互补能力，还是所有人继续成为通才。三个种子仍然只能支持探索性结论，不能包装成确定的 Boids 性能优势。

旧八 agent 批次已完成的种子 71 中性组有 47/48 次成功发布，原始统计 72 个正确跨作者请求，日志归因修正后为 108；Boids 组原始为 600，修正后为 900。两组均无持续单类贡献。中性组一次拒收来自依赖版本声明与实际 import 不一致；Boids 组一次主动 skip。以上是旧反馈条件下的诊断，不能替代修复后的条件比较。

旧批次共花费 581 次 API 请求，未完成独立社会的 114 次也全部计入；输入 2,718,194、输出 182,267、缓存输入 1,995,014 tokens，零 API 错误。94 份已完成社会的发布全部重放，服务成绩不变；两组各六条新增入口干预均确认非崩溃的正确性损失。[中止批次及完整成本](../../studies/tool_ecology/evidence/v03/invalidated-batch-01/inventory.json) · [重放审计](../../studies/tool_ecology/evidence/v03/invalidated-batch-01/summary.json)
