export const translations = {
  zh: {
    app: {
      title: '🚀 GitGuide',
      subtitle: '快速上手任意 GitHub 仓库'
    },
    home: {
      home: '🏠 首页',
      inputPlaceholder: 'https://github.com/user/repo',
      fastMode: '快速模式（约30秒）',
      detailedMode: '详细模式（约2分钟）',
      analyzeBtn: '生成文档',
      analyzing: '分析中...',
      examples: '示例仓库',
      history: '📜 历史记录',
      favorites: '⭐ 收藏仓库',
      clearHistory: '清除历史',
      noHistory: '暂无历史记录',
      noFavorites: '暂无收藏仓库',
      reAnalyze: '重新分析',
      viewDocs: '查看文档',
      remove: '移除'
    },
    docs: {
      title: '文档',
      back: '← 返回首页',
      noResult: '暂无分析结果，请先分析仓库',
      goToAnalyze: '去分析',
      learningDoc: '学习文档',
      setupGuide: '启动指南',
      codeAtlas: '代码图谱',
      aiChat: '💬 AI 问答',
      exportMarkdown: '📥 导出 Markdown',
      exportPDF: '📄 导出 PDF',
      exportHTML: '🌐 导出 HTML',
      favorite: '☆ 收藏',
      favorited: '⭐ 已收藏',
      viewOnGithub: '在 GitHub 查看 →'
    },
    chat: {
      title: 'AI 问答',
      placeholder: '问关于这个项目的问题...',
      send: '发送',
      noContext: '请先分析仓库后再提问'
    },
    common: {
      loading: '加载中...',
      error: '错误',
      success: '成功',
      cancel: '取消',
      confirm: '确认'
    },
    settings: {
      theme: '主题',
      language: '语言',
      light: '浅色',
      dark: '深色'
    }
  },
  en: {
    app: {
      title: '🚀 GitGuide',
      subtitle: 'Quick Start for Any GitHub Repository'
    },
    home: {
      home: '🏠 Home',
      inputPlaceholder: 'https://github.com/user/repo',
      fastMode: 'Fast Mode (~30s)',
      detailedMode: 'Detailed Mode (~2min)',
      analyzeBtn: 'Generate Docs',
      analyzing: 'Analyzing...',
      examples: 'Example Repos',
      history: '📜 History',
      favorites: '⭐ Favorites',
      clearHistory: 'Clear History',
      noHistory: 'No history',
      noFavorites: 'No favorites',
      reAnalyze: 'Re-analyze',
      viewDocs: 'View Docs',
      remove: 'Remove'
    },
    docs: {
      title: 'Documentation',
      back: '← Back to Home',
      noResult: 'No analysis result, please analyze a repo first',
      goToAnalyze: 'Go to Analyze',
      learningDoc: 'Learning Docs',
      setupGuide: 'Setup Guide',
      codeAtlas: 'Code Atlas',
      aiChat: '💬 AI Chat',
      exportMarkdown: '📥 Export Markdown',
      exportPDF: '📄 Export PDF',
      exportHTML: '🌐 Export HTML',
      favorite: '☆ Favorite',
      favorited: '⭐ Favorited',
      viewOnGithub: 'View on GitHub →'
    },
    chat: {
      title: 'AI Chat',
      placeholder: 'Ask questions about this project...',
      send: 'Send',
      noContext: 'Please analyze a repo first'
    },
    common: {
      loading: 'Loading...',
      error: 'Error',
      success: 'Success',
      cancel: 'Cancel',
      confirm: 'Confirm'
    },
    settings: {
      theme: 'Theme',
      language: 'Language',
      light: 'Light',
      dark: 'Dark'
    }
  }
}

// 获取翻译文本
export function t(key, lang = 'zh') {
  const keys = key.split('.')
  let value = translations[lang] || translations.zh

  for (const k of keys) {
    if (value && typeof value === 'object') {
      value = value[k]
    } else {
      return key
    }
  }

  return value || key
}