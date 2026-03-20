<template>
  <div class="repositories-page">
    <div class="header">
      <h1>📚 {{ t('repositories.title', language) }}</h1>
      <p class="subtitle">{{ t('repositories.subtitle', language) }}</p>
    </div>

    <div v-if="loading" class="loading">
      <el-skeleton :rows="5" animated />
    </div>

    <div v-else-if="error" class="error">
      <el-alert type="error" :title="error" show-icon />
    </div>

    <div v-else class="content">
      <div v-if="repositories.length === 0" class="empty-state">
        <el-empty :description="t('repositories.empty', language)">
          <el-button type="primary" @click="$router.push('/')">{{ t('repositories.goToAnalyze', language) }}</el-button>
        </el-empty>
      </div>

      <div v-else class="repo-list">
        <el-card
          v-for="repo in repositories"
          :key="repo.url"
          class="repo-card"
          shadow="hover"
        >
          <template #header>
            <div class="card-header">
              <span class="repo-name">{{ repo.name || repo.url }}</span>
              <el-tag size="small" type="success">{{ repo.language || 'Unknown' }}</el-tag>
            </div>
          </template>

          <div class="card-content">
            <p v-if="repo.description" class="description">{{ repo.description }}</p>
            
            <div class="stats">
              <span>⭐ {{ repo.stars || 0 }}</span>
              <span>📅 {{ formatDate(repo.updated_at) }}</span>
            </div>

            <div class="actions">
              <el-button type="primary" @click="viewRepository(repo)">
                {{ t('repositories.view', language) }}
              </el-button>
              <el-button type="danger" @click="deleteRepository(repo.url)">
                {{ t('repositories.delete', language) }}
              </el-button>
            </div>
          </div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAnalysisStore } from '@/stores/analysis'
import { useSettingsStore } from '@/stores/settings'
import { storeToRefs } from 'pinia'
import { ElMessage, ElMessageBox } from 'element-plus'
import { t } from '@/i18n'

const router = useRouter()
const store = useAnalysisStore()
const settingsStore = useSettingsStore()
const { language } = storeToRefs(settingsStore)

const loading = ref(true)
const error = ref('')
const repositories = ref([])

async function loadRepositories() {
  loading.value = true
  error.value = ''
  
  try {
    const response = await fetch('/api/repositories')
    const data = await response.json()
    
    if (data.repositories) {
      repositories.value = data.repositories
    } else {
      error.value = '加载仓库列表失败'
    }
  } catch (e) {
    error.value = '加载仓库列表失败'
    console.error('Failed to load repositories:', e)
  } finally {
    loading.value = false
  }
}

function viewRepository(repo) {
  store.setRepoUrl(repo.url)
  store.setResult({
    repo_url: repo.url,
    repo_info: {
      name: repo.name,
      description: repo.description,
      language: repo.language,
      stars: repo.stars
    },
    learning_doc: repo.learning_doc,
    setup_guide: repo.setup_guide
  })
  router.push('/docs')
}

async function deleteRepository(url) {
  try {
    await ElMessageBox.confirm(
      t('repositories.deleteConfirm', language),
      t('repositories.deleteTitle', language),
      {
        confirmButtonText: t('common.confirm', language),
        cancelButtonText: t('common.cancel', language),
        type: 'warning'
      }
    )

    const response = await fetch(`/api/repositories/${encodeURIComponent(url)}`, {
      method: 'DELETE'
    })
    const data = await response.json()

    if (data.success) {
      ElMessage.success(t('repositories.deleteSuccess', language))
      await loadRepositories()
    } else {
      ElMessage.error(t('repositories.deleteFailed', language))
    }
  } catch (e) {
    ElMessage.error(t('repositories.deleteFailed', language))
  }
}

function formatDate(dateString) {
  if (!dateString) return '-'
  const date = new Date(dateString)
  return date.toLocaleDateString()
}

onMounted(() => {
  loadRepositories()
})
</script>

<style scoped>
.repositories-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  text-align: center;
  margin-bottom: 40px;
}

.header h1 {
  margin: 0 0 20px 0;
}

.subtitle {
  color: var(--text-color-secondary, #666);
  margin: 0;
}

.loading {
  padding: 40px;
}

.error {
  padding: 20px;
}

.content {
  min-height: 400px;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
}

.repo-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.repo-card {
  transition: transform 0.2s;
}

.repo-card:hover {
  transform: translateY(-4px);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}

.repo-name {
  font-weight: 600;
  font-size: 16px;
}

.card-content {
  padding: 10px 0 0;
}

.description {
  color: var(--text-color-secondary, #666);
  margin: 10px 0;
  font-size: 14px;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.stats {
  display: flex;
  gap: 20px;
  margin: 15px 0;
  font-size: 13px;
  color: var(--text-color-secondary, #666);
}

.actions {
  display: flex;
  gap: 10px;
  margin-top: 15px;
}
</style>
