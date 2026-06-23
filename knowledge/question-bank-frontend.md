# 前端开发题库

---

## JavaScript 核心

### Q1: 闭包
**问题**：什么是闭包？你在项目中怎么用过？
**追问链**：闭包会导致内存泄漏吗？怎么避免？→ 闭包在实际框架中怎么用的？→ 你能写一个用闭包实现的计数器吗？

### Q2: 原型链与继承
**问题**：JavaScript 的继承是怎么实现的？原型链的原理？
**追问链**：`__proto__` 和 `prototype` 的区别？→ ES6 class 和原型继承的关系？→ `instanceof` 的实现原理？

### Q3: 事件循环
**问题**：说说你对 JavaScript 事件循环的理解？微任务和宏任务的区别？
**追问链**：Promise.then 和 setTimeout 谁先执行？→ async/await 的底层实现？→ Node.js 和浏览器的事件循环有什么区别？

---

## 框架原理

### Q4: Vue 响应式原理
**问题**：Vue 3 的响应式是怎么实现的？Proxy 和 defineProperty 的区别？
**追问链**：reactive 和 ref 的区别？→ computed 是怎么实现缓存的？→ watch 和 watchEffect 的区别？→ Vue 3 的 diff 算法做了什么优化？

### Q5: React Hooks 原理
**问题**：React Hooks 解决了什么问题？useState 的底层原理？
**追问链**：为什么 Hooks 不能在条件语句里用？→ useEffect 的依赖数组有什么作用？→ useMemo 和 useCallback 什么时候用？→ 自定义 Hook 你怎么封装的？

---

## 浏览器与网络

### Q6: 浏览器渲染流程
**问题**：从输入 URL 到页面展示，浏览器做了什么？
**追问链**：DOM 树和 CSSOM 树怎么合并成渲染树？→ 重排和重绘的区别？→ 怎么优化首屏加载？→ 你做过哪些性能优化？

### Q7: 跨域
**问题**：什么是跨域？有哪些解决方案？
**追问链**：CORS 的预检请求是什么？→ JSONP 的原理和局限？→ Nginx 反向代理怎么解决跨域？→ Cookie 的 SameSite 属性？

---

## 工程化

### Q8: Webpack / Vite
**问题**：Webpack 的模块打包原理是什么？Vite 为什么比 Webpack 快？
**追问链**：Tree-shaking 怎么实现的？→ 代码分割怎么做的？→ 你写过 Webpack 插件吗？→ Vite 的 ESM 开发模式和 Rollup 打包模式？
