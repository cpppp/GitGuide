import { marked } from 'marked'
import hljs from 'highlight.js'

// 配置 marked
marked.setOptions({
  highlight: function (code, lang) {
    if (lang && hljs.getLanguage(lang)) {
      return hljs.highlight(code, { language: lang }).value
    }
    return code
  }
})

/**
 * 导出为 Markdown
 */
export function exportToMarkdown(result) {
  const repoInfo = result.repo_info || {}
  const content = `# ${repoInfo.full_name || '项目分析报告'}

> 生成时间：${new Date().toLocaleString('zh-CN')}
> 仓库地址：${result.repo_url || ''}

---

## 项目概述

${repoInfo.description || '暂无概述'}

---

## 基本信息

- **语言**: ${repoInfo.language || '未知'}
- **_stars**: ${repoInfo.stargazers_count || 0}
- **Fork 数**: ${repoInfo.forks_count || 0}
- **Watchers**: ${repoInfo.watchers_count || 0}

---

## 快速入门

${result.quick_start || result.learning_doc || '暂无快速入门文档'}

---

## 项目概览

${result.overview || '暂无项目概览文档'}

---

## 架构设计

${result.architecture || '暂无架构设计文档'}

---

## 安装部署

${result.install_guide || result.setup_guide || '暂无安装部署文档'}

---

## 使用教程

${result.usage_tutorial || '暂无使用教程文档'}

---

## 开发指南

${result.dev_guide || '暂无开发指南文档'}

---

## 故障排查

${result.troubleshooting || '暂无故障排查文档'}

---

*本文档由 GitGuide 自动生成*
`
  return content
}

/**
 * 导出为 HTML
 */
export function exportToHTML(result) {
  const markdownContent = exportToMarkdown(result)
  const htmlContent = marked(markdownContent)

  const template = `<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>${(result.repo_info || {}).full_name || '项目分析报告'} - GitGuide</title>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      max-width: 900px;
      margin: 0 auto;
      padding: 40px 20px;
      line-height: 1.6;
      color: #333;
    }
    h1 { font-size: 2em; margin: 0 0 10px; color: #409eff; }
    h2 { font-size: 1.5em; margin: 30px 0 15px; padding-bottom: 10px; border-bottom: 1px solid #eee; }
    h3 { font-size: 1.3em; margin: 20px 0 10px; }
    p { margin: 10px 0; }
    ul, ol { padding-left: 25px; }
    li { margin: 5px 0; }
    code {
      background: #f5f5f5;
      padding: 2px 6px;
      border-radius: 3px;
      font-family: 'Consolas', monospace;
      font-size: 0.9em;
    }
    pre {
      background: #f5f5f5;
      padding: 15px;
      border-radius: 6px;
      overflow-x: auto;
      margin: 15px 0;
    }
    pre code { background: none; padding: 0; }
    blockquote {
      border-left: 4px solid #409eff;
      padding-left: 15px;
      color: #666;
      margin: 15px 0;
    }
    hr { border: none; border-top: 1px solid #eee; margin: 30px 0; }
    a { color: #409eff; text-decoration: none; }
    a:hover { text-decoration: underline; }
    table { border-collapse: collapse; width: 100%; margin: 15px 0; }
    th, td { border: 1px solid #ddd; padding: 10px; text-align: left; }
    th { background: #f5f5f5; }
  </style>
</head>
<body>
  ${htmlContent}
</body>
</html>`

  return template
}

/**
 * 导出为 PDF (使用浏览器打印功能)
 */
export function exportToPDF(result) {
  // 生成 HTML 内容
  const htmlContent = exportToHTML(result)

  // 创建打印窗口
  const printWindow = window.open('', '_blank')
  if (!printWindow) {
    alert('请允许弹出窗口以导出 PDF')
    return
  }

  printWindow.document.write(htmlContent)
  printWindow.document.close()

  // 等待内容加载后触发打印
  printWindow.onload = () => {
    printWindow.print()
  }
}

/**
 * 下载文件
 */
export function downloadFile(content, filename, mimeType = 'text/plain') {
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}