# GitGuide 功能测试指南

> **文档版本**：v1.0  
> **最后更新**：2026-03-20  
> **适用版本**：v3.0 数据持久化版本

---

## 1. 环境准备

### 1.1 安装依赖

```bash
# 进入项目目录
cd d:\@CP\港中文学习资料\课件-港中文第二学期\5660-Agentic_AI\Group-Project\GitGuide-main

# 安装后端依赖
pip install -r requirements.txt

# 安装前端依赖
cd frontend
npm install
cd ..
```

### 1.2 配置环境变量

创建 `.env` 文件（如果不存在）：

```env
# LLM 配置（选择其一）
ZHIPU_API_KEY=your_zhipu_api_key
# 或
OPENAI_API_KEY=your_openai_api_key

# 数据库配置（默认使用 SQLite）
DATABASE_URL=sqlite:///./gitguide.db
```

### 1.3 启动服务

**终端 1 - 启动后端**：
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**终端 2 - 启动前端**：
```bash
cd frontend
npm run dev
```

访问地址：
- 前端：http://localhost:5173
- 后端 API 文档：http://localhost:8000/docs

---

## 2. 基础功能测试

### 2.1 健康检查

**测试步骤**：
1. 打开浏览器访问 http://localhost:8000/api/health
2. 或使用 curl：
   ```bash
   curl http://localhost:8000/api/health
   ```

**预期结果**：
```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### 2.2 首页加载

**测试步骤**：
1. 打开浏览器访问 http://localhost:5173
2. 检查页面是否正常加载

**预期结果**：
- 页面显示 GitGuide 标题
- 显示 URL 输入框
- 显示"生成"按钮
- 显示历史记录区域
- 显示收藏仓库区域

---

## 3. 核心功能测试

### 3.1 仓库分析功能

**测试步骤**：
1. 在首页输入 GitHub 仓库 URL，例如：
   - `https://github.com/vuejs/vue`
   - `https://github.com/facebook/react`
   - `https://github.com/python/cpython`
2. 点击"生成"按钮
3. 观察进度条变化

**预期结果**：
- 进度条正常显示
- 状态提示依次显示：
  - "正在验证仓库..."
  - "正在获取仓库信息..."
  - "正在生成学习文档..."
  - "正在生成启动指南..."
  - "分析完成！"
- 分析完成后自动跳转到文档页面

**测试取消功能**：
1. 开始分析一个仓库
2. 在分析过程中点击"取消"按钮
3. 验证分析是否被取消

**预期结果**：
- 显示"已取消"状态
- 可以重新开始分析

---

### 3.2 文档展示功能

**测试步骤**：
1. 完成仓库分析后，进入文档页面
2. 检查以下内容：
   - 学习文档是否正确渲染
   - 启动指南是否正确渲染
   - Markdown 格式是否正确显示

**预期结果**：
- 文档内容完整
- Markdown 格式正确（标题、列表、代码块等）
- 目录结构清晰

---

### 3.3 AI 问答功能

**测试步骤**：
1. 在文档页面底部找到 AI 问答区域
2. 输入问题，例如：
   - "这个项目如何运行？"
   - "主要使用了哪些技术？"
   - "如何安装依赖？"
3. 点击发送按钮

**预期结果**：
- AI 正确回复问题
- 回复内容与当前仓库相关
- 消息历史正确显示

---

## 4. V3.0 新功能测试

### 4.1 数据库初始化测试

**测试步骤**：
1. 启动后端服务
2. 检查项目根目录是否生成 `gitguide.db` 文件

**预期结果**：
- 数据库文件自动创建
- 后端启动无错误

**手动验证**：
```bash
# 使用 SQLite 命令行工具检查
sqlite3 gitguide.db
.tables
.schema repositories
.quit
```

---

### 4.2 AI 问答记录持久化测试

**测试步骤**：
1. 分析一个仓库
2. 进行多次 AI 问答（至少 3 次）
3. 刷新页面
4. 重新进入该仓库的问答页面

**预期结果**：
- 刷新后问答记录仍然存在
- 问答记录按时间顺序显示
- 用户消息和 AI 回复都正确保存

**API 测试**：
```bash
# 获取问答历史
curl "http://localhost:8000/api/chat/history?repo_url=https://github.com/vuejs/vue"

# 清除问答历史
curl -X DELETE "http://localhost:8000/api/chat/history?repo_url=https://github.com/vuejs/vue"
```

---

### 4.3 仓库文档持久化测试

**测试步骤**：
1. 分析一个仓库
2. 分析完成后，关闭浏览器
3. 重新打开浏览器
4. 访问 API 查看已分析仓库列表

**API 测试**：
```bash
# 获取所有已分析仓库
curl http://localhost:8000/api/repositories

# 获取指定仓库详情
curl "http://localhost:8000/api/repositories/https://github.com/vuejs/vue"

# 删除指定仓库
curl -X DELETE "http://localhost:8000/api/repositories/https://github.com/vuejs/vue"
```

**预期结果**：
- 已分析仓库列表正确返回
- 仓库详情包含 learning_doc 和 setup_guide
- 删除操作成功

---

### 4.4 代码图谱功能测试

**测试步骤**：
1. 完成仓库分析
2. 获取 job_id（从分析响应中）
3. 调用代码图谱 API

**API 测试**：
```bash
# 获取代码图谱（替换 {job_id} 为实际的 job_id）
curl http://localhost:8000/api/analyze/{job_id}/code-graph
```

**预期结果**：
```json
{
  "tree": {
    "name": "仓库名",
    "type": "folder",
    "children": [...]
  },
  "stats": {
    ".js": {"count": 10, "lines": 500},
    ".json": {"count": 2, "lines": 50}
  },
  "dependencies": {
    "imports": ["vue", "axios", ...],
    "modules": [...]
  }
}
```

---

### 4.5 数据导出导入测试

**测试步骤**：

**导出测试**：
```bash
# 导出所有数据
curl http://localhost:8000/api/data/export -o gitguide_export.json
```

**预期结果**：
- 返回 JSON 文件
- 包含 repositories 和 chat_messages 数组

**导入测试**：
```bash
# 导入数据
curl -X POST http://localhost:8000/api/data/import \
  -H "Content-Type: application/json" \
  -d @gitguide_export.json
```

**预期结果**：
```json
{
  "success": true,
  "imported_count": 3
}
```

---

## 5. 历史记录与收藏测试

### 5.1 历史记录

**测试步骤**：
1. 分析多个仓库
2. 检查历史记录列表

**API 测试**：
```bash
# 获取历史记录
curl http://localhost:8000/api/history

# 清除历史记录
curl -X POST http://localhost:8000/api/history/clear
```

**预期结果**：
- 历史记录按时间倒序排列
- 清除后历史记录为空

### 5.2 收藏功能

**测试步骤**：
1. 分析一个仓库
2. 点击收藏按钮
3. 检查收藏列表

**API 测试**：
```bash
# 获取收藏列表
curl http://localhost:8000/api/favorites

# 添加收藏
curl -X POST "http://localhost:8000/api/favorites?repo_url=https://github.com/vuejs/vue"

# 移除收藏
curl -X DELETE "http://localhost:8000/api/favorites?repo_url=https://github.com/vuejs/vue"
```

**预期结果**：
- 收藏成功添加
- 收藏列表正确显示
- 移除收藏成功

---

## 6. 导出功能测试

### 6.1 Markdown 导出

**测试步骤**：
1. 完成仓库分析
2. 点击"导出"按钮
3. 选择 Markdown 格式

**预期结果**：
- 下载 .md 文件
- 文件内容完整，格式正确

### 6.2 HTML 导出

**测试步骤**：
1. 完成仓库分析
2. 点击"导出"按钮
3. 选择 HTML 格式

**预期结果**：
- 下载 .html 文件
- 文件可在浏览器中正确显示

### 6.3 PDF 导出

**测试步骤**：
1. 完成仓库分析
2. 点击"导出"按钮
3. 选择 PDF 格式

**预期结果**：
- 下载 .pdf 文件
- PDF 内容完整，排版正确

---

## 7. 界面功能测试

### 7.1 深色模式

**测试步骤**：
1. 点击右上角主题切换按钮
2. 检查页面颜色变化

**预期结果**：
- 深色模式正常切换
- 所有元素颜色协调
- 主题设置持久化（刷新后保持）

### 7.2 多语言支持

**测试步骤**：
1. 点击语言切换按钮
2. 选择 English/中文

**预期结果**：
- 界面语言正确切换
- 所有文本正确翻译
- 语言设置持久化

---

## 8. 错误处理测试

### 8.1 无效 URL

**测试步骤**：
1. 输入无效的 GitHub URL，例如：
   - `https://github.com/invalid/repo/that/does/not/exist`
   - `not-a-url`
2. 点击生成

**预期结果**：
- 显示错误提示
- 不会崩溃

### 8.2 网络错误

**测试步骤**：
1. 断开网络连接
2. 尝试分析仓库

**预期结果**：
- 显示网络错误提示
- 提供重试选项

### 8.3 API 限流

**测试步骤**：
1. 短时间内多次分析仓库（超过 GitHub API 限制）

**预期结果**：
- 显示限流提示
- 自动等待或提示稍后重试

---

## 9. 性能测试

### 9.1 大型仓库分析

**测试仓库**：
- https://github.com/torvalds/linux
- https://github.com/microsoft/vscode

**测试步骤**：
1. 分析大型仓库
2. 记录分析时间
3. 观察内存使用

**预期结果**：
- 分析在合理时间内完成（< 5 分钟）
- 内存使用稳定
- 无崩溃

### 9.2 并发测试

**测试步骤**：
1. 同时打开多个浏览器标签页
2. 同时分析多个仓库

**预期结果**：
- 所有分析任务正常完成
- 无资源冲突

---

## 10. 测试检查清单

### 基础功能
- [ ] 后端服务正常启动
- [ ] 前端页面正常加载
- [ ] 健康检查 API 正常

### 核心功能
- [ ] 仓库分析功能正常
- [ ] 进度显示正常
- [ ] 取消分析功能正常
- [ ] 文档展示正常
- [ ] AI 问答功能正常

### V3.0 新功能
- [ ] 数据库自动创建
- [ ] AI 问答记录持久化
- [ ] 仓库文档持久化
- [ ] 代码图谱 API 正常
- [ ] 数据导出功能正常
- [ ] 数据导入功能正常

### 辅助功能
- [ ] 历史记录功能正常
- [ ] 收藏功能正常
- [ ] 导出功能正常（MD/HTML/PDF）
- [ ] 深色模式正常
- [ ] 多语言切换正常

### 错误处理
- [ ] 无效 URL 处理正常
- [ ] 网络错误处理正常
- [ ] API 限流处理正常

---

## 11. 常见问题排查

### 问题 1：后端启动失败

**可能原因**：
- 依赖未安装
- 端口被占用
- 环境变量未配置

**解决方案**：
```bash
# 检查依赖
pip install -r requirements.txt

# 检查端口
netstat -ano | findstr :8000

# 检查环境变量
echo %ZHIPU_API_KEY%
```

### 问题 2：数据库错误

**可能原因**：
- 数据库文件权限问题
- SQLAlchemy 版本不兼容

**解决方案**：
```bash
# 删除数据库重新创建
del gitguide.db

# 重新启动后端
python -m uvicorn main:app --reload
```

### 问题 3：AI 问答无响应

**可能原因**：
- API Key 无效
- 网络问题
- LLM 服务不可用

**解决方案**：
- 检查 API Key 是否有效
- 检查网络连接
- 查看后端日志

---

## 12. 测试报告模板

```
## GitGuide 功能测试报告

**测试日期**：YYYY-MM-DD
**测试人员**：
**测试版本**：v3.0

### 测试环境
- 操作系统：Windows 11
- Python 版本：3.x.x
- Node.js 版本：18.x.x
- 浏览器：Chrome 120

### 测试结果汇总
| 功能模块 | 测试用例数 | 通过数 | 失败数 | 通过率 |
|---------|----------|-------|-------|-------|
| 基础功能 | 3 | 3 | 0 | 100% |
| 核心功能 | 5 | 5 | 0 | 100% |
| V3.0新功能 | 6 | 6 | 0 | 100% |
| 辅助功能 | 5 | 5 | 0 | 100% |
| 错误处理 | 3 | 3 | 0 | 100% |

### 问题记录
| 编号 | 问题描述 | 严重程度 | 状态 |
|-----|---------|---------|-----|
| - | - | - | - |

### 测试结论
[通过/不通过]

### 建议
- 建议 1
- 建议 2
```

---

*Last updated: 2026-03-20*
