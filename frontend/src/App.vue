<template>
  <div id="app" :class="['theme-wrapper', { 'dark-theme': isDark }]">
    <!-- 装饰性背景 -->
    <div class="bg-decoration">
      <div class="bg-circle bg-circle-1"></div>
      <div class="bg-circle bg-circle-2"></div>
      <div class="bg-circle bg-circle-3"></div>
      <div class="bg-pattern"></div>
    </div>

    <el-container class="main-container">
      <el-header class="main-header">
        <div class="header-content">
          <div class="logo-section">
            <div class="logo-icon">
              <svg viewBox="0 0 40 40" class="logo-svg">
                <defs>
                  <linearGradient id="logoGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#2c5364" />
                    <stop offset="100%" style="stop-color:#0f2027" />
                  </linearGradient>
                </defs>
                <path d="M20 4 L36 12 L36 28 L20 36 L4 28 L4 12 Z" fill="url(#logoGrad)" opacity="0.15"/>
                <path d="M20 8 L32 14 L32 26 L20 32 L8 26 L8 14 Z" fill="none" stroke="url(#logoGrad)" stroke-width="1.5"/>
                <path d="M14 18 L20 14 L26 18 L26 24 L20 28 L14 24 Z" fill="url(#logoGrad)" opacity="0.6"/>
                <circle cx="20" cy="21" r="3" fill="url(#logoGrad)"/>
              </svg>
            </div>
            <h1 class="logo">{{ t('app.title', language) }}</h1>
          </div>

          <el-menu
            mode="horizontal"
            :default-active="activeMenu"
            router
            class="header-menu"
          >
            <el-menu-item index="/">
              <span class="menu-icon">✦</span>
              {{ t('home.home', language) }}
            </el-menu-item>
            <el-menu-item index="/docs">
              <span class="menu-icon">📖</span>
              {{ t('docs.learningDoc', language) }}
            </el-menu-item>
            <el-menu-item index="/chat">
              <span class="menu-icon">💭</span>
              {{ t('chat.title', language) }}
            </el-menu-item>
          </el-menu>

          <div class="header-actions">
            <el-button class="auth-btn login-btn" text @click="handleLogin">
              {{ language === 'zh' ? '登录' : 'Login' }}
            </el-button>
            <el-button class="auth-btn register-btn" type="primary" @click="handleRegister">
              {{ language === 'zh' ? '注册' : 'Register' }}
            </el-button>
            <!-- 主题切换 -->
            <el-button class="theme-btn" text @click="toggleTheme">
              <span class="theme-icon">{{ isDark ? '◐' : '◑' }}</span>
            </el-button>
            <!-- 语言切换 -->
            <el-dropdown @command="handleLanguageChange" trigger="click">
              <el-button class="lang-btn" text>
                <span class="lang-icon">🌐</span>
                {{ language === 'zh' ? '中' : 'EN' }}
              </el-button>
              <template #dropdown>
                <el-dropdown-menu class="custom-dropdown">
                  <el-dropdown-item command="zh">
                    <span class="dropdown-icon">中</span> 中文
                  </el-dropdown-item>
                  <el-dropdown-item command="en">
                    <span class="dropdown-icon">A</span> English
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </div>
      </el-header>
      <el-main>
        <router-view v-slot="{ Component }">
          <transition name="fade-slide" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </el-main>
      <el-footer class="main-footer">
        <div class="footer-content">
          <div class="footer-left">
            <span class="footer-logo">{{ t('app.title', language) }}</span>
            <span class="footer-divider">|</span>
            <span class="footer-slogan">{{ language === 'zh' ? '快速上手任意 GitHub 仓库' : 'Quick Start Any GitHub Repository' }}</span>
          </div>
          <div class="footer-right">
            <span class="footer-copyright">
              © {{ new Date().getFullYear() }} GitGuide.
              {{ language === 'zh' ? '版权所有' : 'All Rights Reserved' }}.
            </span>
            <span class="footer-separator">|</span>
            <a href="#" class="footer-link">{{ language === 'zh' ? '隐私政策' : 'Privacy Policy' }}</a>
            <span class="footer-separator">|</span>
            <a href="#" class="footer-link">{{ language === 'zh' ? '使用条款' : 'Terms of Use' }}</a>
            <span class="footer-separator">|</span>
            <a href="#" class="footer-link">{{ language === 'zh' ? '联系我们' : 'Contact Us' }}</a>
          </div>
        </div>
      </el-footer>
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

function handleLogin() {
  // Placeholder for login functionality
  console.log('Login clicked')
}

function handleRegister() {
  // Placeholder for register functionality
  console.log('Register clicked')
}
</script>

<style>
/* ========== 学术画本风格主题 ========== */

/* 引入优雅字体 - 使用网络字体 */
@import url('https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600;700&family=Crimson+Pro:ital,wght@0,400;0,600;1,400&family=Noto+Sans+SC:wght@300;400;500&display=swap');

/* CSS 变量 - 浅色学术主题 - 羊皮纸质感 */
:root {
  /* 主色调 - 暖色调学术风 */
  --bg-color: #faf8f5;
  --bg-color-secondary: #ffffff;
  --bg-paper: #fdfcf9;
  --bg-warm: #f5f1eb;

  /* 文字色彩 - 墨色 */
  --text-color: #2c2416;
  --text-color-secondary: #6b5d4d;
  --text-color-muted: #9a8b78;

  /* 边框与分隔 - 淡雅 */
  --border-color: #e8e2d9;
  --border-light: #f0ebe4;

  /* 主色 - 古典墨蓝 */
  --primary-color: #3d5a6c;
  --primary-light: #5a7a8c;
  --primary-dark: #2c3e4a;
  --accent-color: #c4a35a;
  --accent-warm: #b8956e;

  /* 语义色 */
  --success-color: #6b8e6b;
  --warning-color: #c9a227;
  --danger-color: #a65d5d;
  --info-color: #6b8e9f;

  /* 阴影 */
  --shadow-sm: 0 2px 8px rgba(44, 36, 22, 0.06);
  --shadow-md: 0 4px 16px rgba(44, 36, 22, 0.08);
  --shadow-lg: 0 8px 32px rgba(44, 36, 22, 0.12);

  /* 圆角 */
  --radius-sm: 6px;
  --radius-md: 12px;
  --radius-lg: 20px;

  /* 过渡 */
  --transition-fast: 0.2s ease;
  --transition-normal: 0.3s ease;
  --transition-slow: 0.5s ease;

  /* 背景 */
  --header-bg: rgba(253, 252, 249, 0.95);
  --header-shadow: 0 2px 12px rgba(44, 36, 22, 0.06);
}

/* 深色主题 - 夜晚的图书馆 */
.dark-theme {
  --bg-color: #1a1815;
  --bg-color-secondary: #252220;
  --bg-paper: #1e1c19;
  --bg-warm: #2a2622;

  --text-color: #e8e2d9;
  --text-color-secondary: #a0988a;
  --text-color-muted: #706858;

  --border-color: #3a352e;
  --border-light: #332e28;

  --primary-color: #7fa3b8;
  --primary-light: #a3c4d4;
  --primary-dark: #5a7a8c;
  --accent-color: #d4b86a;
  --accent-warm: #c9a66a;

  --success-color: #8fb08f;
  --warning-color: #d4b84a;
  --danger-color: #c47a7a;
  --info-color: #8fb0bf;

  --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.2);
  --shadow-md: 0 4px 16px rgba(0, 0, 0, 0.25);
  --shadow-lg: 0 8px 32px rgba(0, 0, 0, 0.3);

  --header-bg: rgba(30, 28, 25, 0.95);
  --header-shadow: 0 2px 12px rgba(0, 0, 0, 0.2);
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

/* 字体设置 */
body {
  font-family: 'Noto Sans SC', 'Crimson Pro', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
  background-color: var(--bg-color);
  color: var(--text-color);
  min-height: 100vh;
  transition: background-color var(--transition-normal), color var(--transition-normal);
  line-height: 1.7;
  letter-spacing: 0.02em;
}

#app {
  min-height: 100vh;
  position: relative;
}

/* 装饰性背景 */
.theme-wrapper {
  position: relative;
  min-height: 100vh;
}

.bg-decoration {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 0;
  overflow: hidden;
}

.bg-circle {
  position: absolute;
  border-radius: 50%;
  opacity: 0.4;
}

.bg-circle-1 {
  width: 600px;
  height: 600px;
  background: radial-gradient(circle, rgba(196, 163, 90, 0.08) 0%, transparent 70%);
  top: -200px;
  right: -100px;
  animation: float 20s ease-in-out infinite;
}

.bg-circle-2 {
  width: 400px;
  height: 400px;
  background: radial-gradient(circle, rgba(61, 90, 108, 0.06) 0%, transparent 70%);
  bottom: -100px;
  left: -100px;
  animation: float 25s ease-in-out infinite reverse;
}

.bg-circle-3 {
  width: 300px;
  height: 300px;
  background: radial-gradient(circle, rgba(184, 149, 110, 0.06) 0%, transparent 70%);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation: pulse 30s ease-in-out infinite;
}

.bg-pattern {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-image: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23c4a35a' fill-opacity='0.02'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
  opacity: 0.5;
}

@keyframes float {
  0%, 100% { transform: translateY(0) rotate(0deg); }
  50% { transform: translateY(-30px) rotate(5deg); }
}

@keyframes pulse {
  0%, 100% { transform: translate(-50%, -50%) scale(1); opacity: 0.3; }
  50% { transform: translate(-50%, -50%) scale(1.1); opacity: 0.5; }
}

/* 主容器 */
.main-container {
  min-height: 100vh;
  position: relative;
  z-index: 1;
}

/* 头部 */
.main-header {
  background: var(--header-bg);
  backdrop-filter: blur(12px);
  box-shadow: var(--header-shadow);
  padding: 0;
  transition: background-color var(--transition-normal), box-shadow var(--transition-normal);
  border-bottom: 1px solid var(--border-light);
  height: 80px;
  display: flex;
  align-items: center;
}

.header-content {
  display: flex;
  align-items: center;
  max-width: 1200px;
  margin: 0 auto;
  height: 80px;
  padding: 0 24px;
  width: 100%;
}

/* Logo 区域 */
.logo-section {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-right: 48px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.logo-svg {
  width: 100%;
  height: 100%;
}

.logo {
  font-family: 'Noto Serif SC', 'Crimson Pro', Georgia, serif;
  font-size: 26px;
  font-weight: 600;
  color: var(--primary-dark);
  letter-spacing: 0.04em;
  transition: color var(--transition-normal);
}

.dark-theme .logo {
  color: var(--primary-light);
}

/* 导航菜单 */
.header-menu {
  flex: 1;
  border-bottom: none !important;
  background-color: transparent !important;
  height: 80px;
  overflow: visible;
}

.header-menu :deep(.el-menu-item) {
  font-family: 'Noto Sans SC', sans-serif;
  font-size: 15px;
  font-weight: 500;
  height: 80px;
  line-height: 80px;
  padding: 0 20px;
  color: var(--text-color-secondary) !important;
  transition: all var(--transition-normal);
  position: relative;
  border-bottom: none !important;
  display: flex;
  align-items: center;
  justify-content: center;
}

.header-menu :deep(.el-menu-item)::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--accent-color), var(--primary-color));
  border-radius: 3px 3px 0 0;
  transition: width var(--transition-normal);
}

.header-menu :deep(.el-menu-item):hover {
  color: var(--primary-color) !important;
  background: var(--bg-warm) !important;
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
  border-radius: var(--radius-md);
}

.header-menu :deep(.el-menu-item):hover::before {
  display: none !important;
}

.header-menu :deep(.el-menu-item):hover::after {
  width: 60%;
}

/* 修复悬停背景超出导航栏的问题 */
.header-menu :deep(.el-menu) {
  height: 80px;
  border-bottom: none !important;
  display: flex;
  align-items: center;
  overflow: visible;
  position: relative;
}

.header-menu :deep(.el-menu--horizontal) {
  border-bottom: none !important;
  overflow: visible !important;
}

.header-menu :deep(.el-menu-item) {
  position: relative;
  z-index: 1;
}

.header-menu :deep(.el-menu-item.is-active) {
  color: var(--primary-color) !important;
  background-color: transparent !important;
}

.header-menu :deep(.el-menu-item.is-active)::after {
  width: 80%;
}

.menu-icon {
  margin-right: 8px;
  font-size: 14px;
  opacity: 0.8;
}

/* 头部操作区 */
.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-left: auto;
}

.theme-btn,
.lang-btn {
  width: 48px;
  height: 48px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-normal);
  color: var(--text-color-secondary);
}

.theme-btn:hover,
.lang-btn:hover {
  background: var(--bg-warm);
  color: var(--text-color);
}

.theme-icon,
.lang-icon {
  font-size: 18px;
}

.lang-btn {
  width: auto;
  padding: 0 14px;
  gap: 6px;
}

/* 下拉菜单样式 */
.custom-dropdown {
  border-radius: var(--radius-md) !important;
  box-shadow: var(--shadow-lg) !important;
  border: 1px solid var(--border-light) !important;
  padding: 8px !important;
}

.custom-dropdown .el-dropdown-menu__item {
  border-radius: var(--radius-sm);
  padding: 10px 16px;
  font-size: 14px;
  transition: all var(--transition-fast);
}

.dropdown-icon {
  display: inline-block;
  width: 20px;
  height: 20px;
  line-height: 20px;
  text-align: center;
  background: var(--bg-warm);
  border-radius: 4px;
  margin-right: 10px;
  font-size: 12px;
  color: var(--primary-color);
}

/* 主内容区 */
.el-main {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  padding: 32px 24px;
}

/* 页面过渡动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.35s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(20px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-20px);
}

/* ========== Element Plus 组件美化 ========== */

/* 卡片 */
.el-card {
  border: 1px solid var(--border-light) !important;
  border-radius: var(--radius-lg) !important;
  box-shadow: var(--shadow-sm) !important;
  background: var(--bg-paper) !important;
  transition: all var(--transition-normal);
}

.el-card:hover {
  box-shadow: var(--shadow-md) !important;
  border-color: var(--border-color) !important;
}

.el-card__header {
  border-bottom: 1px solid var(--border-light) !important;
  padding: 18px 24px !important;
  font-family: 'Noto Serif SC', serif;
  font-weight: 600;
}

/* 输入框 */
.el-input__wrapper {
  border-radius: var(--radius-md) !important;
  box-shadow: 0 0 0 1px var(--border-color) inset !important;
  background: var(--bg-paper) !important;
  transition: all var(--transition-normal) !important;
  padding: 4px 14px !important;
}

.el-input__wrapper:hover {
  box-shadow: 0 0 0 1px var(--primary-light) inset !important;
}

.el-input__wrapper.is-focus {
  box-shadow: 0 0 0 2px rgba(61, 90, 108, 0.2) inset !important;
  border-color: var(--primary-color) !important;
}

.el-input__inner {
  color: var(--text-color) !important;
  font-size: 15px !important;
}

.el-input__inner::placeholder {
  color: var(--text-color-muted) !important;
}

/* 按钮 */
.el-button {
  border-radius: var(--radius-md) !important;
  font-weight: 500 !important;
  transition: all var(--transition-normal) !important;
  border-color: var(--border-color) !important;
  background: var(--bg-paper) !important;
  color: var(--text-color) !important;
}

.el-button:hover {
  border-color: var(--primary-color) !important;
  color: var(--primary-color) !important;
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.el-button--primary {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark)) !important;
  border-color: var(--primary-color) !important;
  color: #fff !important;
}

.el-button--primary:hover {
  background: linear-gradient(135deg, var(--primary-light), var(--primary-color)) !important;
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* 标签页 */
.el-tabs__header {
  margin-bottom: 24px;
}

.el-tabs__nav-wrap::after {
  background-color: var(--border-light) !important;
}

.el-tabs__item {
  font-size: 15px !important;
  font-weight: 500 !important;
  color: var(--text-color-secondary) !important;
  transition: all var(--transition-normal) !important;
  padding: 0 20px !important;
}

.el-tabs__item:hover {
  color: var(--text-color) !important;
}

.el-tabs__item.is-active {
  color: var(--primary-color) !important;
  font-weight: 600 !important;
}

.el-tabs__active-bar {
  background: linear-gradient(90deg, var(--primary-color), var(--accent-color)) !important;
  height: 3px !important;
  border-radius: 3px !important;
}

/* 标签 */
.el-tag {
  border-radius: var(--radius-sm) !important;
  border: 1px solid var(--border-color) !important;
  background: var(--bg-warm) !important;
  color: var(--text-color-secondary) !important;
  font-size: 13px !important;
  padding: 4px 12px !important;
}

/* 下拉菜单 */
.el-dropdown-menu {
  border-radius: var(--radius-md) !important;
  box-shadow: var(--shadow-lg) !important;
  border: 1px solid var(--border-light) !important;
  padding: 8px !important;
}

.el-dropdown-menu__item {
  border-radius: var(--radius-sm) !important;
  padding: 10px 16px !important;
  transition: all var(--transition-fast) !important;
}

/* 进度条 */
.el-progress-bar__outer {
  border-radius: 10px !important;
  background-color: var(--bg-warm) !important;
}

.el-progress-bar__inner {
  border-radius: 10px !important;
  background: linear-gradient(90deg, var(--primary-color), var(--accent-color)) !important;
}

/* 单选框 */
.el-radio__label {
  color: var(--text-color-secondary) !important;
}

.el-radio__input.is-checked .el-radio__inner {
  background-color: var(--primary-color) !important;
  border-color: var(--primary-color) !important;
}

/* 空状态 */
.el-empty__description {
  color: var(--text-color-muted) !important;
}

/* 警告提示 */
.el-alert {
  border-radius: var(--radius-md) !important;
  border: 1px solid var(--border-light) !important;
}

/* 对话框 */
.el-dialog {
  border-radius: var(--radius-lg) !important;
  box-shadow: var(--shadow-lg) !important;
}

.el-dialog__header {
  border-bottom: 1px solid var(--border-light) !important;
  padding: 20px 24px !important;
}

.el-dialog__title {
  font-family: 'Noto Serif SC', serif;
  font-weight: 600 !important;
  color: var(--text-color) !important;
}

/* 深色模式覆盖 */
.dark-theme {
  /* 输入框 */
  --el-input-bg-color: var(--bg-paper);
  --el-input-border-color: var(--border-color);
  --el-input-text-color: var(--text-color);
  --el-input-placeholder-color: var(--text-color-muted);
}

.dark-theme .el-input__wrapper {
  background-color: var(--bg-paper) !important;
}

.dark-theme .el-button--primary {
  background: linear-gradient(135deg, var(--primary-dark), var(--primary-color)) !important;
}

.dark-theme .el-card {
  background: var(--bg-paper) !important;
}

.dark-theme .el-menu {
  background-color: transparent !important;
}

.dark-theme :deep(.el-menu-item) {
  color: var(--text-color-secondary) !important;
}

.dark-theme :deep(.el-menu-item:hover),
.dark-theme :deep(.el-menu-item.is-active) {
  background-color: var(--bg-warm) !important;
}

.dark-theme .theme-btn:hover,
.dark-theme .lang-btn:hover {
  background: var(--bg-warm);
}

/* 登录/注册按钮 */
.auth-btn {
  font-size: 14px !important;
  font-weight: 500 !important;
  border-radius: var(--radius-md) !important;
  transition: all var(--transition-normal) !important;
}

.login-btn {
  color: var(--text-color-secondary) !important;
}

.login-btn:hover {
  color: var(--primary-color) !important;
  background: var(--bg-warm) !important;
}

.register-btn {
  background: linear-gradient(135deg, var(--primary-color), var(--primary-dark)) !important;
  border-color: var(--primary-color) !important;
  color: #fff !important;
}

.register-btn:hover {
  background: linear-gradient(135deg, var(--primary-light), var(--primary-color)) !important;
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

/* 底部 Footer */
.main-footer {
  background: var(--bg-color-secondary);
  border-top: 1px solid var(--border-light);
  padding: 24px 24px 16px;
  margin-top: auto;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 16px;
  max-width: 1200px;
  margin: 0 auto;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-light);
}

.footer-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.footer-logo {
  font-family: 'Noto Serif SC', serif;
  font-size: 15px;
  font-weight: 600;
  color: var(--primary-dark);
}

.dark-theme .footer-logo {
  color: var(--primary-light);
}

.footer-divider {
  color: var(--border-color);
}

.footer-slogan {
  font-size: 13px;
  color: var(--text-color-muted);
}

.footer-right {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.footer-copyright,
.footer-separator {
  font-size: 12px;
  color: var(--text-color-muted);
}

.footer-link {
  font-size: 12px;
  color: var(--text-color-secondary);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.footer-link:hover {
  color: var(--primary-color);
}

@media (max-width: 768px) {
  .footer-content {
    flex-direction: column;
    text-align: center;
  }

  .footer-left {
    flex-direction: column;
    gap: 6px;
  }

  .footer-divider {
    display: none;
  }

  .footer-right {
    justify-content: center;
  }
}
</style>