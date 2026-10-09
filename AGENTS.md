# 可编辑教学图发布包维护规则

- 本仓库发布 teach-1-plan、teach-2-gen、teach-3-embed、teach-4-ppt；保留简短顺序名。README 是安装和调用的唯一说明入口，不给每个技能另建 README。
- 当前维护原件在提示词系列仓库 .agents/skills。本包由 scripts/sync-skills.cjs 同步，先改原件再同步，不独立维护两套内容。
- 不打包系统/插件技能及第三方 image-to-editable-ppt；在 README 说明依赖来源、安装和实际能力要求。
- 发布前验证技能 frontmatter、全部相对引用、元数据和文件清单；安装与结构验证不冒充真实生图或复现验收。
- 只发布技能、必要规范和维护文档，不发布教学任务包、个人绝对路径、凭据、生成素材或本机扫描报告。
- 用途、目录和安装变化更新 README；进度和验证结果更新项目交接。Git 提交只包含本仓库授权发布内容。
