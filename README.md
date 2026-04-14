# arthas-skills

`arthas-skills` 是一个面向 Arthas MCP 的 Skills，帮助 AI 在排查 Java 应用问题时，按固定的 MCP 地址连接 Arthas，并用更稳定的方式完成诊断。


## 如何安装

如果这个 Skills 已经发布在 Git 仓库中，可以直接用下面的方式安装：

```bash
npx skills add https://github.com/lltx/arthas-skills.git
```

## 安装后验证

进入 CodeX

```bash
$arthas-skills 看一下我的应用的 JVM 占用情况，提供一个分析报告
```

![](https://minio.pigx.vip/oss/202604/skill-test.gif)