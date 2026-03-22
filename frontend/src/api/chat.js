import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 120000
})

export function sendChat(repoUrl, query, history = [], filePath = null) {
  return api.post('/chat', {
    repo_url: repoUrl,
    query: query,
    history: history,
    file_path: filePath
  })
}

export function getChatHistory(repoUrl) {
  return api.get('/chat/history', { params: { repo_url: repoUrl } })
}

export function clearChatHistory(repoUrl) {
  return api.delete('/chat/history', { params: { repo_url: repoUrl } })
}

export function buildKnowledgeBase(repoUrl) {
  return api.post('/chat/build-knowledge-base', null, { params: { repo_url: repoUrl } })
}

export function getFileContent(repoUrl, filePath) {
  return api.get('/chat/file-content', { params: { repo_url: repoUrl, file_path: filePath } })
}
