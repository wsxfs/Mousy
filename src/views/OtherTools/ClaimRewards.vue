<template>
  <div class="claim-rewards">
    <div class="claim-actions">
      <el-checkbox v-model="allSelected" @change="toggleSelectAll">全选</el-checkbox>
      <el-button type="primary" @click="claimAll" :disabled="loading || selectedRowKeys.length === 0">一键领取</el-button>
      <el-button @click="fetchRewards" :disabled="loading">刷新</el-button>
    </div>
    <el-alert v-if="error" :title="error" type="error" show-icon class="mt-2" />
    <el-table
      v-if="rewards.length > 0"
      :data="rewards"
      class="rewards-table"
      @selection-change="handleSelectionChange"
      :row-key="(row: UnclaimedReward) => row.info.id"
      ref="tableRef"
      border
    >
      <el-table-column type="selection" width="50" />
      <el-table-column 
        label="奖励名称" 
        min-width="180"
      >
        <template #default="scope">
          <span>
            {{ formatRewardGroupTitle(scope.row.rewardGroup.localizations.title) }}
          </span>
        </template>
      </el-table-column>
      <el-table-column label="奖励内容" min-width="300">
        <template #default="scope">
          <ul class="reward-items">
            <li v-for="item in scope.row.rewardGroup.rewards" :key="item.id" class="reward-item">
              <div class="reward-item-vertical">
                <template v-if="item.media && typeof item.media.iconUrl === 'string' && item.media.iconUrl">
                  <img v-if="iconBase64Map[item.media.iconUrl]" :src="`data:image/png;base64,${iconBase64Map[item.media.iconUrl]}`" alt="icon" class="reward-icon" />
                  <template v-else>
                    <img :src="item.media.iconUrl" alt="icon" class="reward-icon reward-icon-fallback" @error="onIconError($event, item.media.iconUrl)" v-if="!iconErrorMap[item.media.iconUrl]" />
                    <span v-else class="reward-icon reward-icon-fallback">
                      <svg viewBox="0 0 24 24" width="48" height="48" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="12" cy="12" r="10" stroke="#bbb" stroke-width="2" fill="#f6f6f6"/>
                        <text x="12" y="17" text-anchor="middle" font-size="14" fill="#bbb" font-family="Arial" font-weight="bold">?</text>
                      </svg>
                    </span>
                  </template>
                </template>
                <template v-else>
                  <span class="reward-icon reward-icon-fallback">
                    <svg viewBox="0 0 24 24" width="48" height="48" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <circle cx="12" cy="12" r="10" stroke="#bbb" stroke-width="2" fill="#f6f6f6"/>
                      <text x="12" y="17" text-anchor="middle" font-size="14" fill="#bbb" font-family="Arial" font-weight="bold">?</text>
                    </svg>
                  </span>
                </template>
                <span class="reward-title reward-title-small">{{ item.localizations.title }}</span>
              </div>
            </li>
          </ul>
        </template>
      </el-table-column>
    </el-table>
    <div v-else-if="!loading && !error" class="empty-tip">暂无未领取奖励</div>
    <el-skeleton v-if="loading" rows="4" animated class="skeleton-loading" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, nextTick } from 'vue'
import axios from 'axios'
import type { ElTable } from 'element-plus'

interface RewardItem {
  id: string
  localizations: { title: string }
  quantity: number
  media?: { iconUrl?: string }
}

interface RewardGroup {
  localizations: { title: string; description: string }
  rewards: RewardItem[]
  selectionStrategyConfig: { maxSelectionsAllowed: number; minSelectionsAllowed: number }
}

interface RewardInfo {
  id: string
  rewardGroupId: string
  status: string
}

interface UnclaimedReward {
  info: RewardInfo
  rewardGroup: RewardGroup
}

const rewards = ref<UnclaimedReward[]>([])
const loading = ref(false)
const error = ref('')
const iconBase64Map = ref<Record<string, string>>({})
const selectedRows = ref<UnclaimedReward[]>([])
const selectedRowKeys = computed(() => selectedRows.value.map(row => row.info.id))
const allSelected = ref(false)
const tableRef = ref<InstanceType<typeof ElTable> | null>(null)

// 图标加载失败记录
const iconErrorMap = ref<Record<string, boolean>>({})

let refreshTimer: number | null = null

const fetchRewards = async () => {
  loading.value = true
  error.value = ''
  // 记录当前已选id
  const selectedIds = new Set(selectedRowKeys.value)
  try {
    const res = await axios.get('/api/other_tools/get_unclaimed_rewards')
    if (res.data.success) {
      rewards.value = res.data.data || []
      // 收集所有iconUrl
      const iconUrls = new Set<string>()
      for (const reward of rewards.value) {
        for (const item of reward.rewardGroup.rewards) {
          if (item.media && item.media.iconUrl) {
            iconUrls.add(item.media.iconUrl)
          }
        }
      }
      if (iconUrls.size > 0) {
        // 批量请求base64
        const iconRes = await axios.post('/api/common/game_resource/batch_get_icons_by_url', { urls: Array.from(iconUrls) })
        if (iconRes.data && iconRes.data.icons) {
          iconBase64Map.value = iconRes.data.icons
        }
      }
      await nextTick()
      // 恢复已选
      if (tableRef.value) {
        tableRef.value.clearSelection()
        rewards.value.forEach(row => {
          if (selectedIds.has(row.info.id)) {
            tableRef.value!.toggleRowSelection(row, true)
          }
        })
      }
    } else {
      error.value = res.data.message || '获取奖励失败'
    }
  } catch (e: any) {
    error.value = e.message || '网络错误'
  } finally {
    loading.value = false
  }
}

function handleSelectionChange(val: UnclaimedReward[]) {
  selectedRows.value = val
  allSelected.value = val.length === rewards.value.length && rewards.value.length > 0
}

function toggleSelectAll(val: boolean) {
  allSelected.value = val
  nextTick(() => {
    if (tableRef.value) {
      if (val) {
        tableRef.value.clearSelection()
        rewards.value.forEach(row => tableRef.value!.toggleRowSelection(row, true))
      } else {
        tableRef.value.clearSelection()
      }
    }
  })
}

const claimAll = async () => {
  if (selectedRows.value.length === 0) return
  loading.value = true
  error.value = ''
  try {
    // 构造批量领取参数
    const batchParams = selectedRows.value.map(row => ({
      grantId: row.info.id,
      rewardGroupId: row.info.rewardGroupId,
      rewardIds: row.rewardGroup.rewards.map(item => item.id),
      maxSelectionsAllowed: row.rewardGroup.selectionStrategyConfig.maxSelectionsAllowed
    }))
    const res = await axios.post('/api/other_tools/batch_claim_rewards', batchParams)
    if (res.data && res.data.results) {
      // 领取后刷新奖励列表，也不自动全选
      await fetchRewards()
    } else {
      error.value = '批量领取失败'
    }
  } catch (e: any) {
    error.value = e.message || '批量领取失败'
  } finally {
    loading.value = false
  }
}

function onIconError(event: Event, url: string) {
  if (url) {
    iconErrorMap.value[url] = true
  }
}

// 奖励组标题处理
function formatRewardGroupTitle(title: string) {
  if (title && title.trim().endsWith('DO NOT TRANSLATE')) {
    return '未定义的奖励组'
  }
  return title
}

// 新增：无感刷新函数，只更新rewards数据
const silentRefreshRewards = async () => {
  // 记录当前已选id
  const selectedIds = new Set(selectedRowKeys.value)
  try {
    const res = await axios.get('/api/other_tools/get_unclaimed_rewards')
    if (res.data.success) {
      const newRewards = res.data.data || []
      // 更新iconBase64Map
      const iconUrls = new Set<string>()
      for (const reward of newRewards) {
        for (const item of reward.rewardGroup.rewards) {
          if (item.media && item.media.iconUrl) {
            iconUrls.add(item.media.iconUrl)
          }
        }
      }
      if (iconUrls.size > 0) {
        const iconRes = await axios.post('/api/common/game_resource/batch_get_icons_by_url', { urls: Array.from(iconUrls) })
        if (iconRes.data && iconRes.data.icons) {
          iconBase64Map.value = iconRes.data.icons
        }
      }
      rewards.value = newRewards
      await nextTick()
      // 恢复已选
      if (tableRef.value) {
        tableRef.value.clearSelection()
        rewards.value.forEach(row => {
          if (selectedIds.has(row.info.id)) {
            tableRef.value!.toggleRowSelection(row, true)
          }
        })
      }
    }
  } catch (e) {
    // 静默失败不提示
  }
}

onMounted(() => {
  fetchRewards()
  refreshTimer = window.setInterval(silentRefreshRewards, 1000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
})
</script>

<style scoped>
.claim-rewards {
  max-width: 600px;
  margin: 40px auto 0 auto;
  padding: 32px 24px 24px 24px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 24px #0002;
  min-height: 400px;
}
.claim-title-bar {
  display: flex;
  align-items: flex-end;
  justify-content: center;
  margin-bottom: 24px;
  border-bottom: 1.5px solid #e5e6eb;
  padding-bottom: 10px;
}
.claim-title {
  font-size: 1.7rem;
  font-weight: 600;
  color: #222;
  letter-spacing: 1px;
  font-family: 'Segoe UI', 'PingFang SC', 'Microsoft YaHei', Arial, sans-serif;
  margin: 0;
}
.claim-actions {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 16px;
  margin-bottom: 12px;
}
.rewards-table {
  margin-top: 8px;
  border-radius: 8px;
  overflow: hidden;
  font-size: 14px;
}
.reward-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding-left: 0;
  list-style: none;
  margin: 0;
}
.reward-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 0px;
  padding: 0;
}
/* 新增：竖直排列图标和标题 */
.reward-item-vertical {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
  width: 80px;
  min-height: 70px;
  justify-content: flex-start;
  box-sizing: border-box;
}
.reward-icon {
  width: 48px;
  height: 48px;
  object-fit: contain;
  vertical-align: middle;
  border-radius: 6px;
  box-shadow: 0 1px 4px #0001;
  background: #f6f6f6;
}
.reward-icon-fallback {
  opacity: 0.5;
}
.reward-title {
  font-size: 1rem;
  color: #333;
}
.reward-title-small {
  font-size: 0.62rem;
  color: #666;
  margin-top: 2px;
  text-align: center;
  word-break: break-all;
  line-height: 1.1;
  max-width: 70px;
  min-height: 28px;
  display: flex;
  align-items: flex-start;
  justify-content: center;
}
.empty-tip {
  text-align: center;
  color: #aaa;
  font-size: 1.1rem;
  margin-top: 32px;
}
.skeleton-loading {
  margin-top: 32px;
}
.mt-2 {
  margin-top: 12px;
}
</style> 