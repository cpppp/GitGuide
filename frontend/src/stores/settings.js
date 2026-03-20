import { defineStore } from 'pinia'
import { ref, watch } from 'vue'

export const useSettingsStore = defineStore('settings', () => {
  // 从 localStorage 读取设置
  const getStoredValue = (key, defaultValue) => {
    const stored = localStorage.getItem(key)
    return stored ? JSON.parse(stored) : defaultValue
  }

  // 主题: 'light' | 'dark'
  const theme = ref(getStoredValue('theme', 'light'))

  // 语言: 'zh' | 'en'
  const language = ref(getStoredValue('language', 'zh'))

  // 监听变化并保存到 localStorage
  watch(theme, (newTheme) => {
    localStorage.setItem('theme', JSON.stringify(newTheme))
    applyTheme(newTheme)
  }, { immediate: true })

  watch(language, (newLang) => {
    localStorage.setItem('language', JSON.stringify(newLang))
  })

  // 应用主题
  function applyTheme(themeName) {
    if (themeName === 'dark') {
      document.body.classList.add('dark-theme')
    } else {
      document.body.classList.remove('dark-theme')
    }
  }

  // 切换主题
  function toggleTheme() {
    theme.value = theme.value === 'light' ? 'dark' : 'light'
  }

  // 切换语言
  function setLanguage(lang) {
    language.value = lang
  }

  return {
    theme,
    language,
    toggleTheme,
    setLanguage,
    applyTheme
  }
})