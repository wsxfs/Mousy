<template>
  <div class="match-detail">
    <!-- 添加返回按钮 -->
    <div class="header-controls">
      <el-button 
        type="primary" 
        size="small" 
        @click="$emit('back')"
        :icon="ArrowLeft">
        返回列表
      </el-button>
    </div>

    <!-- 加载状态 -->
    <div v-loading="loading" class="detail-content">
      <template v-if="gameDetail">
        <!-- 在这里添加对局详情的具体内容 -->
        <pre>{{ gameDetail }}</pre>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'

const props = defineProps<{
  gameId: number
}>()

defineEmits<{
  'back': []
}>()

const loading = ref(false)
const gameDetail = ref<any>(null)

// 获取对局详情
const fetchGameDetail = async () => {
  try {
    loading.value = true
    const params = new URLSearchParams()
    params.append('game_id', props.gameId.toString())

    const response = await axios.post(
      '/api/match_history/get_game_detail',
      params,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    )
    
    gameDetail.value = response.data
  } catch (error) {
    console.error('获取对局详情失败:', error)
    ElMessage.error('获取对局详情失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  fetchGameDetail()
})
</script>

<style scoped>
.match-detail {
  padding: 20px;
}

.header-controls {
  margin-bottom: 20px;
}

.detail-content {
  min-height: 200px;
}
</style>
