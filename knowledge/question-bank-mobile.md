# 移动端开发题库

> 按考察维度分类，每个问题附带追问链。面试官根据候选人技术栈选择。

---

## iOS 开发

### Q1: iOS 内存管理
**问题**：iOS 的内存管理机制是什么？ARC 的原理是什么？
**追问链**：
- 循环引用（Retain Cycle）是什么？怎么检测和避免？
- `weak` 和 `unowned` 的区别？分别用在什么场景？
- Autorelease Pool 的工作原理是什么？在什么场景需要手动创建？
- 怎么用 Instruments 排查内存泄漏？

### Q2: iOS 运行时与 UI
**问题**：iOS 的 RunLoop 是什么？它和线程的关系？
**追问链**：
- RunLoop 的 Mode 有哪些？默认 Mode 和 Tracking Mode 的区别？
- UITableView 的复用机制是什么？Cell 复用出问题怎么排查？
- iOS 的渲染流程是怎样的？卡顿的原因和优化手段？
- Swift 的值类型和引用类型有什么区别？struct 和 class 怎么选？

---

## Android 开发

### Q3: Android 四大组件与生命周期
**问题**：Activity 的生命周期有哪些？异常情况下生命周期是怎么变化的？
**追问链**：
- Activity 被系统回收后怎么恢复状态？`onSaveInstanceState` 怎么用？
- Fragment 和 Activity 的生命周期是怎么关联的？
- Service 的 `startService` 和 `bindService` 有什么区别？
- BroadcastReceiver 的有序广播和普通广播的区别？Android 8.0 后的限制？

### Q4: Android 性能优化
**问题**：Android App 启动优化你做过吗？从哪些方面入手？
**追问链**：
- 冷启动和热启动的区别？怎么测量启动时间？
- 内存泄漏怎么排查？LeakCanary 的原理是什么？
- 列表卡顿怎么优化？RecyclerView 的优化技巧有哪些？
- APK 包体积怎么优化？用过哪些手段？

### Q5: Android 架构与 Jetpack
**问题**：你们 Android 项目用的是什么架构？MVVM 怎么实现的？
**追问链**：
- ViewModel 是怎么在配置变更（如屏幕旋转）后存活的？
- LiveData 和 Flow 的区别？数据倒灌问题怎么解决？
- Room 数据库的版本升级怎么处理？
- Hilt / Dagger 依赖注入的原理是什么？

---

## 跨平台开发

### Q6: Flutter 核心机制
**问题**：Flutter 的渲染机制是什么？Widget、Element、RenderObject 三棵树的关系？
**追问链**：
- StatelessWidget 和 StatefulWidget 的区别？State 的生命周期？
- Flutter 的 BuildContext 是什么？它和 Element 的关系？
- Flutter 的平台通道（Platform Channel）怎么和原生通信？
- Flutter 的性能问题一般出在哪里？怎么用 DevTools 排查？

### Q7: React Native
**问题**：React Native 的通信机制是什么？旧架构（Bridge）和新架构（Fabric/TurboModule）的区别？
**追问链**：
- RN 的 JS 线程和 Native 线程怎么协作？
- FlatList 的性能优化怎么做？和 ScrollView 的区别？
- RN 项目中原生模块（Native Module）怎么编写？
- RN 的热更新（Code Push）原理是什么？

---

## 移动端性能与工程化

### Q8: 网络优化与数据安全
**问题**：移动端网络请求优化的策略有哪些？
**追问链**：
- HTTP 缓存策略怎么设计？弱网环境怎么优化？
- 接口请求的合并和优先级怎么管理？
- 移动端的 HTTPS 证书校验怎么做？怎么防止抓包？
- 数据加密传输方案是什么？对称加密和非对称加密怎么结合？

### Q9: 工程化与发布
**问题**：你们的移动端 CI/CD 流程是怎样的？
**追问链**：
- 多渠道打包怎么实现？签名管理怎么做？
- 灰度发布和 A/B Test 怎么实现？
- 线上 Crash 监控和收集方案是什么？怎么分析 Crash 堆栈？
- 组件化 / 模块化架构怎么设计？模块间通信方案是什么？

---

## 评价维度

| 维度 | 优秀表现 | 不合格表现 |
|------|---------|-----------|
| 平台基础 | 深入理解平台机制（内存/生命周期/渲染） | 只会调 API，不理解底层原理 |
| 跨平台 | 理解框架原理，能解决复杂兼容问题 | 只写过简单页面，不会排查平台差异 |
| 性能优化 | 有系统优化经验，能用工具定位瓶颈 | 无优化思路，不会使用分析工具 |
| 工程化 | 搭建过 CI/CD，有模块化经验 | 手动打包发布，无工程化意识 |
