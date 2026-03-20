<template>
  <div id="app" :class="{ 'dark-theme': isDark }">
    <el-container class="main-container">
      <el-header class="main-header">
        <div class="header-content">
          <h1 class="logo">{{ t('app.title', language) }}</h1>
          <el-menu
            mode="horizontal"
            :default-active="activeMenu"
            router
            class="header-menu"
          >
            <el-menu-item index="/">{{ t('home.home', language) || '🏠 Home' }}</el-menu-item>
            <el-menu-item index="/docs">{{ t('docs.learningDoc', language) || '📚 Docs' }}</el-menu-item>
            <el-menu-item index="/chat">{{ t('chat.title', language) }}</el-menu-item>
          </el-menu>
          <div class="header-actions">
            <!-- 主题切换 -->
            <el-button text @click="toggleTheme">
              {{ isDark ? '☀️' : '🌙' }}
            </el-button>
            <!-- 语言切换 -->
            <el-dropdown @command="handleLanguageChange">
              <el-button text>
                {{ language === 'zh' ? '中文' : 'EN' }}
              </el-button>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item command="zh">中文</el-dropdown-item>
                  <el-dropdown-item command="en">English</el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useSettingsStore } from '@/stores/settings'
import { storeToRefs } from 'pinia'
import { t } from '@/i18n'

const route = useRoute()
const settingsStore = useSettingsStore()
const { theme, language } = storeToRefs(settingsStore)
const { toggleTheme, setLanguage } = settingsStore

const isDark = computed(() => theme.value === 'dark')

const activeMenu = computed(() => route.path)

function handleLanguageChange(lang) {
  setLanguage(lang)
}
</script>

<style>
/* CSS 变量 - 浅色主题 */
:root {
  --bg-color: #f5f7fa;
  --bg-color-secondary: #ffffff;
  --text-color: #303133;
  --text-color-secondary: #606266;
  --border-color: #dcdfe6;
  --primary-color: #409eff;
  --header-bg: #ffffff;
}

/* 深色主题 */
.dark-theme {
  --bg-color: #1a1a1a;
  --bg-color-secondary: #2d2d2d;
  --text-color: #e0e0e0;
  --text-color-secondary: #a0a0a0;
  --border-color: #404040;
  --primary-color: #409eff;
  --header-bg: #2d2d2d;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: var(--bg-color);
  color: var(--text-color);
  min-height: 100vh;
  transition: background-color 0.3s, color 0.3s;
}

#app {
  min-height: 100vh;
}

.main-container {
  min-height: 100vh;
}

.main-header {
  background-color: var(--header-bg);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0;
  transition: background-color 0.3s;
}

.header-content {
  display: flex;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  height: 100%;
}

.logo {
  font-size: 24px;
  margin-right: 40px;
  color: var(--primary-color);
}

.header-menu {
  flex: 1;
  border-bottom: none !important;
  background-color: transparent !important;
}

.header-menu .el-menu-item {
  background-color: transparent !important;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-left: auto;
}

.el-main {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  padding: 20px;
}

/* 深色模式下的 Element Plus 覆盖 */
.dark-theme .el-card {
  background-color: var(--bg-color-secondary);
  color: var(--text-color);
  border-color: var(--border-color);
}

.dark-theme .el-input__wrapper {
  background-color: var(--bg-color-secondary);
  box-shadow: 0 0 0 1px var(--border-color) inset;
}

.dark-theme .el-input__inner {
  color: var(--text-color);
}

.dark-theme .el-button {
  background-color: var(--bg-color-secondary);
  border-color: var(--border-color);
  color: var(--text-color);
}

.dark-theme .el-button--primary {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
  color: #fff;
}

.dark-theme .el-menu {
  background-color: transparent;
  border-color: var(--border-color);
}

.dark-theme .el-menu-item {
  color: var(--text-color);
}

.dark-theme .el-menu-item:hover,
.dark-theme .el-menu-item.is-active {
  background-color: var(--bg-color) !important;
}

.dark-theme .el-tabs__item {
  color: var(--text-color-secondary);
}

.dark-theme .el-tabs__item.is-active {
  color: var(--primary-color);
}

.dark-theme .el-dropdown-menu {
  background-color: var(--bg-color-secondary);
  border-color: var(--border-color);
}

.dark-theme .el-dropdown-menu__item {
  color: var(--text-color);
}

.dark-theme .el-dropdown-menu__item:hover {
  background-color: var(--bg-color);
  color: var(--primary-color);
}

.dark-theme .el-empty__description p {
  color: var(--text-color-secondary);
}

.dark-theme .el-tag {
  background-color: var(--bg-color);
  border-color: var(--border-color);
  color: var(--text-color);
}

.dark-theme .el-progress__text {
  color: var(--text-color);
}

.dark-theme .el-radio__label {
  color: var(--text-color);
}

.dark-theme .el-alert {
  background-color: var(--bg-color-secondary);
}

.dark-theme .el-dialog {
  background-color: var(--bg-color-secondary);
  color: var(--text-color);
}

.dark-theme .el-message-box {
  background-color: var(--bg-color-secondary);
  color: var(--text-color);
}
</style>