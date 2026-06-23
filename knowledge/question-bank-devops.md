# DevOps / SRE 题库

> 按考察维度分类，每个问题附带追问链。面试官根据候选人技术栈选择。

---

## Linux 与 Shell

### Q1: Linux 基础与排障
**问题**：线上服务器 CPU 飙高到 100%，你怎么排查？
**追问链**：
- `top` 命令的输出怎么解读？`%wa` 高说明什么问题？
- 怎么定位到具体是哪个进程、哪个线程导致的 CPU 高？
- `strace` 和 `perf` 分别在什么场景使用？
- 服务器 Load Average 很高但 CPU 使用率不高，什么原因？

### Q2: Shell 脚本与自动化
**问题**：你写过哪些运维脚本？Shell 脚本的调试技巧有哪些？
**追问链**：
- `set -e`、`set -u`、`set -o pipefail` 分别是什么作用？
- 怎么用 Shell 实现日志轮转和清理？
- 怎么在 Shell 中处理 JSON 数据？jq 用过吗？
- Shell 脚本和 Python 脚本做运维你会怎么选择？

---

## 容器与 Kubernetes

### Q3: Docker 容器
**问题**：Docker 镜像的分层机制是什么？怎么优化镜像大小？
**追问链**：
- Dockerfile 的 `COPY` 和 `ADD` 有什么区别？多阶段构建怎么用？
- 容器的资源限制（CPU/内存）怎么配置？超出限制会怎样？
- Docker 的网络模式有哪些？bridge 和 host 模式的区别？
- 容器内的进程和宿主机进程是什么关系？Namespace 和 Cgroups 的作用？

### Q4: Kubernetes 核心概念
**问题**：K8s 中 Pod、Deployment、Service 三者的关系是什么？
**追问链**：
- Pod 的生命周期有哪些阶段？`Init Container` 和普通容器有什么区别？
- Deployment 的滚动更新策略怎么配置？回滚怎么操作？
- Service 的类型有哪些？ClusterIP、NodePort、LoadBalancer 的区别？
- HPA（水平自动扩缩容）的原理是什么？基于什么指标触发？

### Q5: K8s 运维与排障
**问题**：Pod 一直处于 Pending 状态，你怎么排查？
**追问链**：
- `kubectl describe pod` 和 `kubectl logs` 分别能看到什么信息？
- K8s 的调度策略有哪些？亲和性和反亲和性怎么配置？
- ConfigMap 和 Secret 的区别？Secret 真的安全吗？
- K8s 集群的网络方案了解哪些？Calico 和 Flannel 的区别？

---

## CI/CD

### Q6: CI/CD 流水线设计
**问题**：你搭建过 CI/CD 流水线吗？用的什么工具？完整的流水线包含哪些环节？
**追问链**：
- Jenkins 的 Pipeline as Code（Jenkinsfile）怎么写？声明式和脚本式的区别？
- GitLab CI 的 `.gitlab-ci.yml` 怎么组织？stages 和 jobs 的关系？
- 怎么实现蓝绿部署和金丝雀发布？各有什么优缺点？
- 流水线中的代码质量门禁（Quality Gate）怎么设计？

### Q7: Git 工作流与分支策略
**问题**：你们团队用的是什么 Git 工作流？分支策略怎么设计的？
**追问链**：
- Git Flow 和 Trunk-Based Development 各适合什么团队？
- 代码合并冲突怎么处理？rebase 和 merge 的区别？
- Git Hooks 怎么用来做代码规范检查？pre-commit 框架用过吗？
- 多环境（dev/staging/prod）的发布流程怎么管理？

---

## 监控与告警

### Q8: 监控体系
**问题**：你们线上用的什么监控方案？监控体系是怎么搭建的？
**追问链**：
- Prometheus 的 Pull 模型和 Push 模型有什么区别？PromQL 怎么写？
- Grafana 的 Dashboard 怎么设计？你关注哪些核心指标？
- 日志方案用的什么？ELK 和 Loki 各有什么优缺点？
- 分布式链路追踪（Jaeger/Zipkin）的原理是什么？TraceID 怎么传递？

### Q9: 告警与故障处理
**问题**：告警风暴怎么处理？怎么设计有效的告警规则？
**追问链**：
- 告警的分级策略怎么设计？P0-P3 各代表什么？
- 告警抑制和告警收敛是什么？怎么实现？
- SLO、SLI、SLA 分别是什么？Error Budget 怎么用？
- 线上出了故障，你的应急响应流程是怎样的？事后复盘怎么做？

---

## 评价维度

| 维度 | 优秀表现 | 不合格表现 |
|------|---------|-----------|
| Linux 基础 | 能快速定位系统问题，熟练使用排查工具 | 只会基础命令，不会分析性能问题 |
| 容器与 K8s | 深入理解 K8s 架构，有集群运维经验 | 仅会简单操作，不理解原理 |
| CI/CD | 能设计完整流水线，实践过多种部署策略 | 只会点按钮触发构建 |
| 监控告警 | 搭建过完整监控体系，有故障处理经验 | 没有监控意识，不会写 PromQL |
