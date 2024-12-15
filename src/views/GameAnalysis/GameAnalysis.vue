<template>
  <div class="game-analysis">
    <div class="analysis-container">
      <!-- 搜索区域 -->
      <div class="search-section">
        <h2>对局成分分析</h2>
        <div class="search-box">
          <el-input
            v-model="searchQuery"
            placeholder="输入对局ID"
            class="search-input"
            clearable
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-button type="primary" @click="handleSearch" :loading="loading">
            查询
          </el-button>
        </div>
      </div>

      <!-- 结果展示区域 -->
      <div v-if="searchPerformed" class="result-section">
        <el-empty v-if="!loading && !hasResults" description="未找到相关信息" />
        <!-- 这里后续会添加查询结果的展示 -->
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const searchQuery = ref('')
const loading = ref(false)
const searchPerformed = ref(false)
const hasResults = ref(false)

const handleSearch = async () => {
  if (!searchQuery.value.trim()) {
    ElMessage.warning('请输入对局ID')
    return
  }

  loading.value = true
  searchPerformed.value = true
  
  try {
    // TODO: 实现查询逻辑
    hasResults.value = false // 暂时设置为false
  } catch (error) {
    console.error('查询失败:', error)
    ElMessage.error('查询失败，请稍后重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.game-analysis {
  padding: 20px;
  height: 100%;
  box-sizing: border-box;
}

.analysis-container {
  max-width: 1200px;
  margin: 0 auto;
  background-color: var(--el-bg-color-overlay);
  border-radius: 8px;
  box-shadow: var(--el-box-shadow-light);
  padding: 24px;
}

.search-section {
  margin-bottom: 24px;
}

.search-section h2 {
  margin: 0 0 16px 0;
  color: var(--el-text-color-primary);
  font-size: 24px;
}

.search-box {
  display: flex;
  gap: 12px;
  max-width: 600px;
}

.search-input {
  flex: 1;
}

.result-section {
  min-height: 200px;
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 响应式布局 */
@media (max-width: 768px) {
  .game-analysis {
    padding: 12px;
  }

  .analysis-container {
    padding: 16px;
  }

  .search-box {
    flex-direction: column;
  }
}
</style> 