import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000
})

// 发送问答请求
export function sendChat(repoUrl, query, history = []) {
  return api.post('/chat', {
    repo_url: repoUrl,
    query: query,
    history: history
  })
}