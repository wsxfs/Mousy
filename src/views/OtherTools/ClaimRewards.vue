<template>
  <div class="claim-rewards">
    <h2>领取奖励</h2>
    <el-checkbox v-model="allSelected" @change="toggleSelectAll" style="margin-bottom: 8px;">全选</el-checkbox>
    <el-button type="primary" @click="claimAll" :disabled="loading || selectedRowKeys.length === 0" style="margin-left: 8px;">一键领取</el-button>
    <el-alert v-if="error" :title="error" type="error" show-icon class="mt-2" />
    <el-table
      v-if="rewards.length > 0"
      :data="rewards"
      style="width: 100%; margin-top: 16px;"
      @selection-change="handleSelectionChange"
      :row-key="(row: UnclaimedReward) => row.info.id"
      ref="tableRef"
    >
      <el-table-column type="selection" width="50" />
      <el-table-column prop="info.id" label="grantId" width="180" />
      <el-table-column prop="info.rewardGroupId" label="rewardGroupId" width="180" />
      <el-table-column prop="rewardGroup.selectionStrategyConfig.maxSelectionsAllowed" label="maxSelectionsAllowed" width="80" />
      <el-table-column prop="rewardGroup.selectionStrategyConfig.minSelectionsAllowed" label="minSelectionsAllowed" width="80" />
      <el-table-column prop="rewardGroup.localizations.title" label="标题" />
      <el-table-column label="奖励内容">
        <template #default="scope">
          <ul style="padding-left:0;list-style:none;">
            <li v-for="item in scope.row.rewardGroup.rewards" :key="item.id" style="display:flex;align-items:center;gap:8px;">
              <template v-if="item.media && item.media.iconUrl">
                <img v-if="iconBase64Map[item.media.iconUrl]" :src="`data:image/png;base64,${iconBase64Map[item.media.iconUrl]}`" alt="icon" style="width:24px;height:24px;object-fit:contain;vertical-align:middle;" />
                <img v-else :src="item.media.iconUrl" alt="icon" style="width:24px;height:24px;object-fit:contain;vertical-align:middle;opacity:0.5;" />
              </template>
              <span>{{ item.localizations.title }} × {{ item.quantity }}（id: {{ item.id }}）</span>
            </li>
          </ul>
        </template>
      </el-table-column>
    </el-table>
    <div v-else-if="!loading && !error" class="mt-2">暂无未领取奖励</div>
    <el-skeleton v-if="loading" rows="4" animated style="margin-top: 16px;" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
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

const fetchRewards = async () => {
  loading.value = true
  error.value = ''
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
      // 默认全选
      if (rewards.value.length > 0) {
        toggleSelectAll(true)
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
      // 可根据res.data.results做进一步处理或提示
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

onMounted(fetchRewards)
</script>

<style scoped>
.claim-rewards {
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px #0001;
}
.mt-2 {
  margin-top: 12px;
}
</style> 