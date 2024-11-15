<template>
  <div class="champion-detail">
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

    <!-- 克制关系部分 -->
    <div class="section">
      <h3>英雄克制</h3>
      <div class="counters-container">
        <!-- 强势对线 -->
        <div class="counter-group">
          <h4>强势对线</h4>
          <div class="counter-list">
            <div v-for="champion in championDetail?.counters?.strongAgainst"
                 :key="champion.championId"
                 class="counter-item">
              <img :src="getResourceUrl('champion_icons', champion.championId)" 
                   class="counter-icon"
                   :title="champion.name">
              <div class="counter-stats">
                <div class="champion-name">{{ champion.name }}</div>
                <div class="win-rate">胜率: {{ (champion.winRate * 100).toFixed(1) }}%</div>
                <div class="play-count">对局: {{ champion.play }}</div>
              </div>
            </div>
          </div>
        </div>

        <!-- 劣势对线 -->
        <div class="counter-group">
          <h4>劣势对线</h4>
          <div class="counter-list">
            <div v-for="champion in championDetail?.counters?.weakAgainst"
                 :key="champion.championId"
                 class="counter-item">
              <img :src="getResourceUrl('champion_icons', champion.championId)" 
                   class="counter-icon"
                   :title="champion.name">
              <div class="counter-stats">
                <div class="champion-name">{{ champion.name }}</div>
                <div class="win-rate">胜率: {{ (champion.winRate * 100).toFixed(1) }}%</div>
                <div class="play-count">对局: {{ champion.play }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 召唤师技能部分 -->
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

    <!-- 技能加点部分 -->
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
        
        <!-- 详细加点顺序 -->
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

    <!-- 出装部分 -->
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

        <!-- 鞋子选择 -->
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

    <!-- 符文部分 -->
    <div class="section">
      <h3>符文配置</h3>
      <div class="runes-container">
        <div v-for="(rune, index) in championDetail?.perks"
             :key="index"
             class="rune-set">
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
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  championId: number
}>()

const championDetail = ref<any>(null)
const gameResources = ref<any>({})
const version = ref<string>('')
const mode = ref<string>('')

// 格式化百分比
const formatPercent = (value: number) => {
  return value ? `${(value * 100).toFixed(1)}%` : '0%'
}

// 获取资源URL
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
    const resourceRequest = {
      champion_icons: [props.championId] as number[],  // 初始化时包含当前英雄
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

      // 添加召唤师技能图标
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
    gameResources.value = response.data
  } catch (error) {
    console.error('加载游戏资源失败:', error)
    ElMessage.error('加载游戏资源失败')
  }
}

// 获取英雄详细数据
const fetchChampionDetail = async () => {
  try {
    const params = new URLSearchParams({
      champion_id: props.championId.toString(),
      region: 'kr',
      mode: 'ranked',
      position: 'TOP',
      tier: 'platinum_plus'
    })

    const response = await axios.post(
      '/api/match_data/champion_build',
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
    await loadGameResources()
  } catch (error) {
    ElMessage.error('获取英雄详情失败')
    console.error('获取英雄详情失败:', error)
  }
}

// 监听championId变化
watch(() => props.championId, () => {
  fetchChampionDetail()
})

onMounted(() => {
  fetchChampionDetail()
})
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
}

.counter-icon {
  width: 40px;
  height: 40px;
  border-radius: 50%;
}

.counter-stats {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.champion-name {
  font-weight: bold;
}

.win-rate {
  color: var(--el-color-success);
  font-size: 14px;
}

.play-count {
  color: var(--el-text-color-secondary);
  font-size: 12px;
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

/* 响应式布局调整 */
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
</style>