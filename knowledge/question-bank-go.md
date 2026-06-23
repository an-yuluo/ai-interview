# Go 后端开发题库

> 按考察维度分类，每个问题附带追问链。面试官根据候选人技术栈选择。

---

## Goroutine 与并发

### Q1: Goroutine 基础与调度
**问题**：Goroutine 和线程有什么区别？Go 是怎么实现轻量级并发的？
**追问链**：
- Goroutine 的栈是怎么管理的？和线程栈有什么不同？
- Go 的 GMP 调度模型是什么？G、M、P 分别代表什么？
- 如果一个 Goroutine 里发生了死循环，会影响其他 Goroutine 吗？为什么？
- `runtime.Gosched()` 和 `time.Sleep()` 的区别是什么？

### Q2: Channel 与并发模式
**问题**：Channel 的底层数据结构是什么？有缓冲和无缓冲 Channel 有什么区别？
**追问链**：
- Channel 在什么情况下会阻塞？底层是怎么实现阻塞的？
- `select` 语句的机制是什么？多个 case 同时就绪时怎么选择？
- 用过哪些 Go 并发模式？（fan-in / fan-out / worker pool / pipeline）
- 怎么用 Channel 实现一个生产者-消费者模型？怎么处理优雅退出？

### Q3: 并发安全与同步
**问题**：Go 里有哪些并发同步手段？各自适用什么场景？
**追问链**：
- `sync.Mutex` 和 `sync.RWMutex` 的底层实现了解吗？
- `sync.WaitGroup` 的原理是什么？有没有踩过坑？
- `sync.Once` 是怎么保证只执行一次的？底层用了什么机制？
- `atomic` 包和 Mutex 相比有什么优势？什么场景用 atomic？

---

## Go Runtime

### Q4: 垃圾回收（GC）
**问题**：Go 的垃圾回收用的是什么算法？经历了哪些版本演进？
**追问链**：
- 三色标记法的过程是什么？怎么解决并发标记时的数据竞争？
- 混合写屏障（Hybrid Write Barrier）是什么？解决了什么问题？
- Go GC 的触发条件有哪些？GOGC 环境变量的作用？
- 线上服务 GC 频繁怎么排查和优化？

### Q5: Interface 与反射
**问题**：Go 的 interface 是怎么实现的？iface 和 eface 有什么区别？
**追问链**：
- 类型断言的底层原理是什么？为什么类型断言失败会 panic？
- 空接口 `interface{}` 为什么可以接收任意类型？有什么性能代价？
- `reflect` 包的使用场景和性能问题你了解吗？
- Go 的泛型（Type Parameter）和 interface 相比有什么优劣？

---

## 错误处理与编程模式

### Q6: 错误处理
**问题**：Go 的错误处理方式为什么采用返回值而不是异常？你怎么看这种设计？
**追问链**：
- `error` 接口的底层是什么？自定义 error 怎么实现？
- `errors.Is()` 和 `errors.As()` 的用法和区别？
- Go 1.13 的 `%w` 格式化包装错误是什么？错误链怎么工作？
- `panic` 和 `recover` 的机制是什么？什么场景下应该用 panic？

### Q7: Context 与超时控制
**问题**：`context` 包的作用是什么？有哪几种 Context 类型？
**追问链**：
- `context.WithCancel` 和 `context.WithTimeout` 的底层实现原理？
- Context 是怎么在 Goroutine 树中传播取消信号的？
- 在 HTTP 请求链路中，Context 是怎么传递和使用的？
- Context 的 Value 方法有什么使用注意事项？为什么不建议存大量数据？

---

## 性能分析与优化

### Q8: pprof 性能分析
**问题**：你用过 Go 的 pprof 工具吗？怎么对线上服务做性能分析？
**追问链**：
- CPU profile 和 Memory profile 分别怎么采集？
- pprof 的火焰图怎么看？你分析过哪些性能瓶颈？
- trace 工具了解吗？和 pprof 有什么区别？
- Go 的逃逸分析（escape analysis）是什么？怎么减少堆分配？

### Q9: Go 项目工程实践
**问题**：你做过 Go 项目的性能优化吗？从哪些方面入手？
**追问链**：
- `sync.Pool` 的原理和使用场景是什么？
- Go 的内存对齐了解吗？struct 字段顺序对性能有影响吗？
- 怎么做 Go 服务的压测？你关注哪些指标？
- Go 的编译优化手段有哪些？（内联、循环展开、PGO 等）

---

## 评价维度

| 维度 | 优秀表现 | 不合格表现 |
|------|---------|-----------|
| 并发编程 | 深入理解 GMP 模型，能设计复杂并发方案 | 仅会用 go 关键字，不理解调度原理 |
| Runtime | 清楚 GC 演进和调优，能排查 GC 问题 | 不了解 GC 机制，无法分析内存问题 |
| 错误处理 | 遵循 Go 惯例，错误链清晰，防御性编程 | 忽略 error，panic 滥用 |
| 性能优化 | 熟练使用 pprof，有系统优化经验 | 不会性能分析工具，无优化思路 |
