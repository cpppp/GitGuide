<template>
  <div id="app">
    <el-container class="main-container">
      <el-header class="main-header">
        <div class="header-content">
          <h1 class="logo">🚀 GitGuide</h1>
          <el-menu
            mode="horizontal"
            :default-active="activeMenu"
            router
            class="header-menu"
          >
            <el-menu-item index="/">🏠 首页</el-menu-item>
            <el-menu-item index="/docs">📚 文档</el-menu-item>
            <el-menu-item index="/chat">💬 问答</el-menu-item>
          </el-menu>
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

const route = useRoute()

const activeMenu = computed(() => route.path)
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  background-color: #f5f7fa;
  min-height: 100vh;
}

#app {
  min-height: 100vh;
}

.main-container {
  min-height: 100vh;
}

.main-header {
  background-color: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0;
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
  color: #409eff;
}

.header-menu {
  flex: 1;
  border-bottom: none !important;
}

.el-main {
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  padding: 20px;
}
</style>