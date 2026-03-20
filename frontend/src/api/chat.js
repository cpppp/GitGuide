import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000
})

export function sendChat(repoUrl, query, history = []) {
  return api.post('/chat', {
    repo_url: repoUrl,
    query: query,
    history: history
  })
}

export function getChatHistory(repoUrl) {
  return api.get('/chat/history', { params: { repo_url: repoUrl } })
}

export function clearChatHistory(repoUrl) {
  return api.delete('/chat/history', { params: { repo_url: repoUrl } })
}
