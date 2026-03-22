import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 300000
})

// 启动分析
export function startAnalyze(repoUrl) {
  return api.post('/analyze', {
    repo_url: repoUrl
  })
}

// 获取任务状态
export function getTaskStatus(jobId) {
  return api.get(`/analyze/${jobId}/status`)
}

// 取消分析
export function cancelAnalysis(jobId) {
  return api.post(`/analyze/${jobId}/cancel`)
}

// 获取历史记录
export function getHistory() {
  return api.get('/history')
}

// 清除历史记录
export function clearHistory() {
  return api.post('/history/clear')
}

// 获取收藏列表
export function getFavorites() {
  return api.get('/favorites')
}

// 添加收藏
export function addFavorite(repoUrl) {
  return api.post('/favorites', null, { params: { repo_url: repoUrl } })
}

// 移除收藏
export function removeFavorite(repoUrl) {
  return api.delete('/favorites', { params: { repo_url: repoUrl } })
}

// WebSocket 连接
export function createWebSocket(jobId) {
  // 使用相对路径，通过 Vite 代理连接到后端
  // 后端路由是 /api/ws/analyze/{job_id}
  const wsUrl = `/api/ws/analyze/${jobId}`
  return new WebSocket(wsUrl)
}