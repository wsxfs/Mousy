<template>
  <div class="champion-detail">
    <!-- 添加回到顶部按钮 -->
    <el-backtop :right="20" :bottom="20" target=".champion-detail">
      <el-icon><ArrowUpBold /></el-icon>
    </el-backtop>
    
    <!-- 修改头部控制区域的结构和样式 -->
    <div class="header-controls">
      <div class="left-controls">
        <el-button 
          type="primary" 
          size="small" 
          @click="$emit('back')"
          icon="ArrowLeft">
          返回列表
        </el-button>
      </div>
      
      <div class="right-controls">
        <!-- 添加服务器选择 -->
        <el-select 
          v-model="selectedRegion" 
          placeholder="选择服务器" 
          @change="handleFilterChange"
          size="small"
          style="width: 120px;">
          <el-option label="韩服" value="kr" />
          <el-option label="欧服" value="euw" />
          <el-option label="美服" value="na" />
        </el-select>

        <!-- 添加段位选择 -->
        <el-select 
          v-model="selectedTier" 
          placeholder="选择段位" 
          @change="handleFilterChange"
          size="small"
          style="width: 120px;">
          <el-option label="全部" value="all" />
          <el-option label="青铜" value="bronze" />
          <el-option label="白银" value="silver" />
          <el-option label="黄金" value="gold" />
          <el-option label="黄金及以上" value="gold_plus" />
          <el-option label="铂金" value="platinum" />
          <el-option label="铂金及以上" value="platinum_plus" />
          <el-option label="钻石" value="diamond" />
          <el-option label="钻石及以上" value="diamond_plus" />
          <el-option label="大师" value="master" />
          <el-option label="大师及以上" value="master_plus" />
          <el-option label="宗师" value="grandmaster" />
          <el-option label="王者" value="challenger" />
        </el-select>

        <!-- 修改位置选择器,只显示可用位置 -->
        <el-radio-group 
          v-model="selectedPosition" 
          @change="handleFilterChange"
          size="small">
          <el-radio-button 
            v-for="position in availablePositions" 
            :key="position" 
            :label="position">
            {{ getPositionLabel(position) }}
          </el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <!-- 基本信息部分 -->
    <div class="summary-section">
      <div class="champion-basic-info">
        <img :src="getResourceUrl('champion_icons', championDetail?.summary?.championId)" class="champion-avatar">
        <div class="champion-stats">
          <h2>{{ championDetail?.summary?.name }}</h2>
          <div class="stats-grid">
            <div class="stat-item">
              <span class="label">胜率</span>
              <span class="value">{{ formatPercent(championDetail?.summary?.winRate) }}</span>
            </div>
            <div class="stat-item">
              <span class="label">登场率</span>
              <span class="value">{{ formatPercent(championDetail?.summary?.pickRate) }}</span>
            </div>
            <div class="stat-item">
              <span class="label">禁用率</span>
              <span class="value">{{ formatPercent(championDetail?.summary?.banRate) }}</span>
            </div>
            <div class="stat-item">
              <span class="label">KDA</span>
              <span class="value">{{ championDetail?.summary?.kda?.toFixed(2) }}</span>
            </div>
          </div>
        </div>
      </div>
      <!-- 添加版本和模式信息 -->
      <div class="version-info">
        <span>版本: {{ version }}</span>
        <span>模式: {{ mode === 'ranked' ? '排位赛' : '匹配模式' }}</span>
      </div>
    </div>

    <!-- 1. 符文部分 -->
    <div class="section">
      <div class="section-header">
        <h3>符文配置</h3>
        <el-button 
          type="primary" 
          size="small"
          :disabled="selectedRuneIndex === null"
          @click="applyRunes">
          应用符文
        </el-button>
      </div>
      <div class="runes-container">
        <div v-for="(rune, index) in championDetail?.perks"
             :key="index"
             :class="['rune-set', { 'selected': selectedRuneIndex === index }]"
             @click="selectedRuneIndex = index">
          <div class="rune-trees">
            <img :src="getResourceUrl('perk_icons', rune.primaryId)" class="tree-icon">
            <img :src="getResourceUrl('perk_icons', rune.secondaryId)" class="tree-icon">
          </div>
          <div class="rune-icons">
            <img v-for="icon in rune.icons"
                 :key="icon"
                 :src="getResourceUrl('perk_icons', icon)"
                 class="rune-icon">
          </div>
          <div class="rune-stats">
            <span>胜率: {{ (rune.win / rune.play * 100).toFixed(1) }}%</span>
            <span>使用率: {{ (rune.pickRate * 100).toFixed(1) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 2. 出装部分 -->
    <div class="section">
      <h3>推荐出装</h3>
      <div class="items-container">
        <!-- 起始装备 -->
        <div class="item-group">
          <h4>起始装备</h4>
          <div v-for="(build, index) in championDetail?.items?.startItems"
               :key="index"
               class="build-row">
            <div class="item-icons">
              <img v-for="icon in build.icons"
                   :key="icon"
                   :src="getResourceUrl('item_icons', icon)"
                   class="item-icon">
            </div>
            <div class="build-stats">
              <span>胜率: {{ (build.win / build.play * 100).toFixed(1) }}%</span>
              <span>使用率: {{ (build.pickRate * 100).toFixed(1) }}%</span>
            </div>
          </div>
        </div>

        <!-- 鞋子择 -->
        <div class="item-group">
          <h4>鞋子选择</h4>
          <div v-for="(build, index) in championDetail?.items?.boots"
               :key="index"
               class="build-row">
            <div class="item-icons">
              <img v-for="icon in build.icons"
                   :key="icon"
                   :src="getResourceUrl('item_icons', icon)"
                   class="item-icon">
            </div>
            <div class="build-stats">
              <span>胜率: {{ (build.win / build.play * 100).toFixed(1) }}%</span>
              <span>使用率: {{ (build.pickRate * 100).toFixed(1) }}%</span>
              <span>场次: {{ build.play }}</span>
            </div>
          </div>
        </div>

        <!-- 核心装备 -->
        <div class="item-group">
          <h4>核心装备</h4>
          <div v-for="(build, index) in championDetail?.items?.coreItems"
               :key="index"
               class="build-row">
            <div class="item-icons">
              <img v-for="icon in build.icons"
                   :key="icon"
                   :src="getResourceUrl('item_icons', icon)"
                   class="item-icon">
            </div>
            <div class="build-stats">
              <span>胜率: {{ (build.win / build.play * 100).toFixed(1) }}%</span>
              <span>使用率: {{ (build.pickRate * 100).toFixed(1) }}%</span>
            </div>
          </div>
        </div>

        <!-- 添加最终装备列表 -->
        <div class="item-group">
          <h4>可选装备池</h4>
          <div class="last-items-grid">
            <div v-for="itemId in championDetail?.items?.lastItems"
                 :key="itemId"
                 class="last-item">
              <img :src="getResourceUrl('item_icons', itemId)"
                   class="item-icon"
                   :title="itemId">
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 3. 唤师技能部分 -->
    <div class="section">
      <h3>召唤师技能</h3>
      <div class="summoner-spells">
        <div v-for="(spell, index) in championDetail?.summonerSpells" 
             :key="index"
             class="spell-group">
          <div class="spell-icons">
            <img v-for="icon in spell.icons" 
                 :key="icon"
                 :src="getResourceUrl('summoner_spell_icons', icon)"
                 class="spell-icon">
          </div>
          <div class="spell-stats">
            <span>胜率: {{ (spell.win / spell.play * 100).toFixed(1) }}%</span>
            <span>使用率: {{ (spell.pickRate * 100).toFixed(1) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 4. 技能加点部分 -->
    <div class="section">
      <h3>技能加点</h3>
      <div class="skill-order" v-if="championDetail?.championSkills">
        <!-- 主系技能 -->
        <div class="skill-masteries">
          <h4>主系技能</h4>
          <div class="mastery-sequence">
            <div v-for="(skill, index) in championDetail.championSkills.masteries" 
                 :key="index"
                 class="mastery-item">
              {{ skill }}
            </div>
          </div>
        </div>
        
        <!-- 详细点顺序 -->
        <div class="skill-sequence-container">
          <h4>加点顺序</h4>
          <div class="skill-sequence">
            <div v-for="(skill, index) in championDetail.championSkills.order" 
                 :key="index"
                 class="skill-item">
              {{ skill }}
            </div>
          </div>
          <div class="skill-stats">
            <span>胜率: {{ (championDetail.championSkills.win / championDetail.championSkills.play * 100).toFixed(1) }}%</span>
            <span>使用率: {{ (championDetail.championSkills.pickRate * 100).toFixed(1) }}%</span>
            <span>场次: {{ championDetail.championSkills.play }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 5. 克制关系部分 -->
    <div class="section">
      <h3>英雄克制</h3>
      <div class="counters-container">
        <!-- 强势对 -->
        <div class="counter-group strong">
          <h4>强势对线</h4>
          <div class="counter-list">
            <div v-for="champion in championDetail?.counters?.strongAgainst"
                 :key="champion.championId"
                 class="counter-item"
                 @click="$emit('champion-click', champion.championId, champion.name)">
              <img :src="getResourceUrl('champion_icons', champion.championId)" 
                   class="counter-icon"
                   :title="champion.name">
              <div class="counter-info">
                <span class="champion-name">{{ champion.name }}</span>
                <span class="win-rate" :class="{ win: champion.winRate > 0.5, lose: champion.winRate < 0.5 }">
                  胜率 {{ (champion.winRate * 100).toFixed(1) }}%
                </span>
                <span class="play-count">{{ champion.play }}场</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 劣势对线 -->
        <div class="counter-group weak">
          <h4>劣势对线</h4>
          <div class="counter-list">
            <div v-for="champion in championDetail?.counters?.weakAgainst"
                 :key="champion.championId"
                 class="counter-item"
                 @click="$emit('champion-click', champion.championId, champion.name)">
              <img :src="getResourceUrl('champion_icons', champion.championId)" 
                   class="counter-icon"
                   :title="champion.name">
              <div class="counter-info">
                <span class="champion-name">{{ champion.name }}</span>
                <span class="win-rate" :class="{ win: champion.winRate > 0.5, lose: champion.winRate < 0.5 }">
                  胜率 {{ (champion.winRate * 100).toFixed(1) }}%
                </span>
                <span class="play-count">{{ champion.play }}场</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import { ArrowLeft, ArrowUpBold } from '@element-plus/icons-vue'

const props = defineProps<{
  championId: number,
  initialPosition?: string,
  initialTier?: string,
  initialRegion?: string
}>()

const championDetail = ref<any>(null)
const gameResources = ref<any>({})
const version = ref<string>('')
const mode = ref<string>('')

// 选中的符文页索引
const selectedRuneIndex = ref<number | null>(null)

// 添加段位状态
const selectedTier = ref(props.initialTier || 'platinum_plus')
const selectedPosition = ref(props.initialPosition || 'TOP')

// 添加服务器状态
const selectedRegion = ref(props.initialRegion || 'kr')

// 添加可用位置状态
const availablePositions = ref<string[]>([])

// 添加位置标签映射
const positionLabels: Record<string, string> = {
  TOP: '上路',
  JUNGLE: '打野', 
  MID: '中路',
  ADC: '下路',
  SUPPORT: '辅助'
}

// 获取位置显示标签
const getPositionLabel = (position: string) => {
  return positionLabels[position] || position
}

// 应用符文的方法
const applyRunes = async () => {
  if (selectedRuneIndex.value === null) {
    ElMessage.warning('先选择一个符文配置')
    return
  }

  try {
    const selectedRune = championDetail.value.perks[selectedRuneIndex.value]
    const winRate = (selectedRune.win / selectedRune.play * 100).toFixed(1)
    const pickRate = (selectedRune.pickRate * 100).toFixed(1)
    
    // 准备符文数据，简化命名式
    const perksData = {
      name: `${championDetail.value.summary.name}|胜率${winRate}%|使用率${pickRate}%(Best Wishes From Mousy🐹)`,
      primary_style_id: selectedRune.primaryId,
      sub_style_id: selectedRune.secondaryId,
      selected_perk_ids: selectedRune.perks
    }

    // 调用应用符文接口
    const response = await axios.post('/api/match_data/match_data/apply_perks', perksData)
    
    if (response.data.success) {
      ElMessage.success('符文应用成功')
    } else {
      ElMessage.error(response.data.message || '符文应用失败')
    }
  } catch (error: any) {
    console.error('应用符文失败:', error)
    ElMessage.error('应用符文失败：' + (error.response?.data?.detail || error.message))
  }
}

// 格式化百分比
const formatPercent = (value: number) => {
  return value ? `${(value * 100).toFixed(1)}%` : '0%'
}

// 获资源URL
const getResourceUrl = (type: string, id: number): string => {
  const typeMapping: Record<string, string> = {
    'champion_icons': 'champion_icons',
    'summoner_spell_icons': 'spell_icons',
    'item_icons': 'item_icons',
    'perk_icons': 'rune_icons'
  }

  const backendType = typeMapping[type]
  const resources = gameResources.value[backendType]
  if (resources?.[id]) {
    return `data:image/png;base64,${resources[id]}`
  }
  return '/placeholder.png'
}

// 加载游戏资源
const loadGameResources = async () => {
  try {
    // 确保 championDetail 存在且有效
    if (!championDetail.value) {
      return
    }

    const resourceRequest = {
      champion_icons: [props.championId] as number[],
      spell_icons: [] as number[],
      item_icons: [] as number[],
      rune_icons: [] as number[]
    }
    
    // 收集所需的资源ID
    if (championDetail.value) {
      // 添加克制关系英雄图标
      championDetail.value.counters?.strongAgainst?.forEach((champion: any) => {
        if (!resourceRequest.champion_icons.includes(champion.championId)) {
          resourceRequest.champion_icons.push(champion.championId)
        }
      })
      
      championDetail.value.counters?.weakAgainst?.forEach((champion: any) => {
        if (!resourceRequest.champion_icons.includes(champion.championId)) {
          resourceRequest.champion_icons.push(champion.championId)
        }
      })

      // 添加召唤师技图标
      championDetail.value.summonerSpells?.forEach((spell: any) => {
        spell.icons.forEach((id: number) => {
          if (!resourceRequest.spell_icons.includes(id)) {
            resourceRequest.spell_icons.push(id)
          }
        })
      })

      // 添加装备图标
      const items = championDetail.value.items
      ;['startItems', 'coreItems', 'boots'].forEach((category) => {
        items[category]?.forEach((build: any) => {
          build.icons.forEach((id: number) => {
            if (!resourceRequest.item_icons.includes(id)) {
              resourceRequest.item_icons.push(id)
            }
          })
        })
      })

      // 添加 lastItems 的图标收集
      items.lastItems?.forEach((itemId: number) => {
        if (!resourceRequest.item_icons.includes(itemId)) {
          resourceRequest.item_icons.push(itemId)
        }
      })

      // 添加符文图标
      championDetail.value.perks?.forEach((perk: any) => {
        ;[perk.primaryId, perk.secondaryId, ...perk.icons].forEach((id: number) => {
          if (!resourceRequest.rune_icons.includes(id)) {
            resourceRequest.rune_icons.push(id)
          }
        })
      })
    }

    const response = await axios.post('/api/common/game_resource/batch_get_resources', resourceRequest)
    // 清空旧资源后再设置新资源
    gameResources.value = {}
    gameResources.value = response.data
  } catch (error) {
    console.error('加载游戏资源失败:', error)
    ElMessage.error('加载游戏资源失败')
  }
}

// 添加数据加载状态
const isLoading = ref(false)

// 获取英雄详细数据
const fetchChampionDetail = async () => {
  try {
    isLoading.value = true
    // 重置符文选择
    selectedRuneIndex.value = null
    // 清空旧数据和资源
    championDetail.value = null
    gameResources.value = {}
    
    const params = new URLSearchParams({
      champion_id: props.championId.toString(),
      region: selectedRegion.value,
      mode: 'ranked',
      position: selectedPosition.value,
      tier: selectedTier.value
    })

    const response = await axios.post(
      '/api/match_data/match_data/champion_build',
      params,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    )

    championDetail.value = response.data.data
    version.value = response.data.version
    mode.value = response.data.mode
    // 在设置新数据后加载资源
    await loadGameResources()
  } catch (error) {
    ElMessage.error('获取英雄详情失败')
    console.error('获取英雄详情失败:', error)
  } finally {
    isLoading.value = false
  }
}

// 获取英雄可用位置
const fetchAvailablePositions = async () => {
  try {
    isLoading.value = true
    // 重置符文选择
    selectedRuneIndex.value = null
    // 清空旧数据
    championDetail.value = null
    
    const params = new URLSearchParams({
      champion_id: props.championId.toString(),
      region: selectedRegion.value,
      tier: selectedTier.value
    })

    const response = await axios.post(
      '/api/match_data/match_data/champion_positions',
      params,
      {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded'
        }
      }
    )

    availablePositions.value = response.data
    
    // 如当前选择的位置不在可用位置中,选择第一个可用位置
    if (!availablePositions.value.includes(selectedPosition.value)) {
      selectedPosition.value = availablePositions.value[0]
    }
    
    // 在设置好位置后获取英雄详情
    await fetchChampionDetail()
  } catch (error) {
    console.error('获取英雄可用位置失败:', error)
    ElMessage.error('获取英雄可用位置失败')
  } finally {
    isLoading.value = false
  }
}

// 统一的筛选条件变更处理函数
const handleFilterChange = () => {
  // 如果是段位变更，需要重新获取可用位置
  if (selectedTier.value !== props.initialTier) {
    fetchAvailablePositions()
  } else {
    // 如果只是位置变更，直接获取详情即可
    fetchChampionDetail()
  }
}

// 监听 championId 变化
watch(() => props.championId, () => {
  fetchAvailablePositions()
})

onMounted(() => {
  fetchAvailablePositions()
})

// 新 emit 定义
defineEmits<{
  back: []
  'champion-click': [championId: number, name: string]
  'position-change': [position: string]
}>()
</script>

<style scoped>
.champion-detail {
  padding: 20px;
  height: 100%;
  overflow-y: auto;
}

.section {
  margin-bottom: 30px;
  background: var(--el-bg-color);
  border-radius: 8px;
  padding: 20px;
  box-shadow: var(--el-box-shadow-lighter);
}

.summary-section {
  margin-bottom: 30px;
}

.champion-basic-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.champion-avatar {
  width: 80px;
  height: 80px;
  border-radius: 50%;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  margin-top: 10px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.label {
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.value {
  font-size: 16px;
  font-weight: bold;
}

/* 召唤师技能样式 */
.summoner-spells {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 20px;
}

.spell-group {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.spell-icons {
  display: flex;
  gap: 5px;
}

.spell-icon {
  width: 40px;
  height: 40px;
  border-radius: 4px;
}

/* 能加点样式 */
.skill-sequence {
  display: flex;
  gap: 5px;
  margin-bottom: 10px;
}

.skill-item {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--el-color-primary-light-9);
  border-radius: 4px;
  font-weight: bold;
}

/* 装备样式 */
.items-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.item-group {
  margin-bottom: 20px;
}

.build-row {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 10px;
}

.item-icons {
  display: flex;
  gap: 5px;
}

.item-icon {
  width: 40px;
  height: 40px;
  border-radius: 4px;
}

/* 符文样式 */
.runes-container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
}

.rune-set {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.rune-trees {
  display: flex;
  gap: 10px;
}

.tree-icon {
  width: 40px;
  height: 40px;
}

.rune-icons {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.rune-icon {
  width: 30px;
  height: 30px;
}

/* 通用统计信息样式 */
.build-stats,
.spell-stats,
.skill-stats,
.rune-stats {
  display: flex;
  gap: 15px;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

/* 克制关系样式 */
.counters-container {
  display: flex;
  gap: 30px;
}

.counter-group {
  flex: 1;
}

.counter-list {
  max-height: 500px;
  overflow-y: auto;
  padding-right: 10px;
}

.counter-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px;
  background: var(--el-bg-color-page);
  border-radius: 6px;
  cursor: pointer;
  transition: transform 0.2s ease, background-color 0.2s ease;
}

.counter-item:hover {
  transform: translateX(5px);
  background-color: var(--el-color-primary-light-9);
}

.counter-group.strong .counter-item:hover {
  background-color: var(--el-color-success-light-8);
}

.counter-group.weak .counter-item:hover {
  background-color: var(--el-color-danger-light-8);
}

.counter-icon {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  flex-shrink: 0;
}

.counter-info {
  flex: 1;
  display: grid;
  grid-template-columns: 3fr 3fr 1.9fr;
  align-items: center;
}

.champion-name {
  font-weight: bold;
  font-size: 14px;
  padding-left: 1px;
}

.win-rate {
  color: var(--el-text-color-secondary);
  font-size: 14px;
  text-align: right;
  padding-right: 20px;
}

.play-count {
  color: var(--el-text-color-secondary);
  font-size: 13px;
  text-align: left;
  padding-left: 20px;
}

.win-rate.win {
  color: var(--el-color-success);
}

.win-rate.lose {
  color: var(--el-color-danger);
}

/* 技能加点样式补充 */
.skill-masteries {
  margin-bottom: 20px;
}

.mastery-sequence {
  display: flex;
  gap: 10px;
  margin-top: 10px;
}

.mastery-item {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--el-color-primary-light-8);
  border-radius: 4px;
  font-weight: bold;
  font-size: 18px;
}

.skill-sequence-container {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

/* 美化滚动条 */
.counter-list::-webkit-scrollbar {
  width: 6px;
}

.counter-list::-webkit-scrollbar-thumb {
  background-color: var(--el-border-color-darker);
  border-radius: 3px;
}

.counter-list::-webkit-scrollbar-track {
  background-color: var(--el-border-color-light);
  border-radius: 3px;
}

/* 响应式布局调 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .runes-container,
  .summoner-spells {
    grid-template-columns: 1fr;
  }
  
  .counter-list {
    max-height: 300px;
  }
}

/* 最终装备列表样式 */
.last-items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(40px, 1fr));
  gap: 10px;
  margin-top: 10px;
}

.last-item {
  display: flex;
  justify-content: center;
  align-items: center;
}

/* 响应式布局调整 */
@media (max-width: 768px) {
  .last-items-grid {
    grid-template-columns: repeat(auto-fill, minmax(40px, 1fr));
  }
}

.version-info {
  margin-top: 10px;
  display: flex;
  gap: 20px;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.rune-set {
  cursor: pointer;
  border: 2px solid transparent;
  border-radius: 8px;
  padding: 10px;
  transition: all 0.3s ease;
}

.rune-set:hover {
  background: var(--el-color-primary-light-9);
}

.rune-set.selected {
  border-color: var(--el-color-primary);
  background: var(--el-color-primary-light-9);
}

/* 添加返回按钮容器样式 */
.back-button-container {
  margin-bottom: 20px;
}

/* 克制关系样式更新 */
.counter-group.strong .counter-item {
  background: var(--el-color-success-light-9);
  border-left: 4px solid var(--el-color-success);
}

.counter-group.weak .counter-item {
  background: var(--el-color-danger-light-9);
  border-left: 4px solid var(--el-color-danger);
}

.counter-item {
  margin-bottom: 10px;
  transition: transform 0.2s ease;
}

.counter-item:hover {
  transform: translateX(5px);
}

.win-rate.win {
  color: var(--el-color-success);
  font-weight: bold;
}

.win-rate.lose {
  color: var(--el-color-danger);
  font-weight: bold;
}

.counter-group h4 {
  margin-bottom: 15px;
  padding-bottom: 8px;
  border-bottom: 2px solid var(--el-border-color-light);
}

.counter-group.strong h4 {
  color: var(--el-color-success);
}

.counter-group.weak h4 {
  color: var(--el-color-danger);
}

/* 添加回到顶部按钮样式 */
:deep(.el-backtop) {
  background-color: var(--el-color-primary);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background-color 0.3s;
}

:deep(.el-backtop:hover) {
  background-color: var(--el-color-primary-light-3);
}

/* 更新头部控制区域样式 */
.header-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 10px;
  background-color: var(--el-bg-color-overlay);
  border-radius: 8px;
  box-shadow: var(--el-box-shadow-lighter);
}

.left-controls {
  display: flex;
  align-items: center;
}

.right-controls {
  display: flex;
  gap: 15px;
  align-items: center;
}

/* 调整选择器样式 */
:deep(.el-select) {
  margin-right: 10px;
}

:deep(.el-radio-group) {
  margin-left: 10px;
}

/* 响应式布局调整 */
@media (max-width: 768px) {
  .header-controls {
    flex-direction: column;
    gap: 10px;
  }
  
  .right-controls {
    flex-direction: column;
    width: 100%;
  }
  
  :deep(.el-select) {
    width: 100%;
    margin-right: 0;
    margin-bottom: 10px;
  }
  
  :deep(.el-radio-group) {
    width: 100%;
    margin-left: 0;
    display: flex;
    justify-content: space-between;
  }
}
</style>