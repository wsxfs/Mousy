<template>
    <div class="match-data">
      <!-- 位置选择器 -->
      <div class="position-selector">
        <el-radio-group v-model="selectedPosition" @change="handlePositionChange">
          <el-radio-button label="TOP">上路</el-radio-button>
          <el-radio-button label="JUNGLE">打野</el-radio-button>
          <el-radio-button label="MID">中路</el-radio-button>
          <el-radio-button label="ADC">下路</el-radio-button>
          <el-radio-button label="SUPPORT">辅助</el-radio-button>
        </el-radio-group>
      </div>
  
      <!-- 筛选条件 -->
      <div class="filter-section">
        <el-form :inline="true" :model="filterForm">
          <el-form-item label="段位">
            <el-select v-model="filterForm.tier" placeholder="选择段位">
              <el-option label="铂金以上" value="platinum_plus" />
              <el-option label="钻石以上" value="diamond_plus" />
              <el-option label="大师以上" value="master_plus" />
            </el-select>
          </el-form-item>
          <el-form-item label="模式">
            <el-select v-model="filterForm.mode" placeholder="选择模式">
              <el-option label="单双排位" value="ranked" />
              <el-option label="匹配模式" value="normal" />
            </el-select>
          </el-form-item>
        </el-form>
      </div>
  
      <!-- 英雄列表 -->
      <div class="champion-tier-list">
        <el-table :data="championList" style="width: 100%">
          <el-table-column label="英雄" width="200">
            <template #default="scope">
              <div class="champion-info">
                <img :src="`data:image/png;base64,${scope.row.icon}`" class="champion-icon">
                <span>{{ scope.row.name }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column prop="winRate" label="胜率" width="100">
            <template #default="scope">
              {{ (scope.row.winRate * 100).toFixed(1) }}%
            </template>
          </el-table-column>
          <el-table-column prop="pickRate" label="登场率" width="100">
            <template #default="scope">
              {{ (scope.row.pickRate * 100).toFixed(1) }}%
            </template>
          </el-table-column>
          <el-table-column prop="banRate" label="禁用率" width="100">
            <template #default="scope">
              {{ (scope.row.banRate * 100).toFixed(1) }}%
            </template>
          </el-table-column>
          <el-table-column label="克制英雄" width="200">
            <template #default="scope">
              <div class="counter-champions">
                <img 
                  v-for="counter in scope.row.counters" 
                  :key="counter.championId"
                  :src="`data:image/png;base64,${counter.icon}`" 
                  class="counter-icon"
                >
              </div>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </div>
  </template>
  
  <script setup lang="ts">
  import { ref, onMounted, watch } from 'vue'
  import axios from 'axios'
  import { ElMessage } from 'element-plus'
  
  // 接口定义
  interface Champion {
    championId: number
    name: string
    icon: string
    winRate: number
    pickRate: number
    banRate: number
    kda: number
    tier: number
    rank: number
    position: string
    counters: Array<{
      championId: number
      icon: string
    }>
  }
  
  // 状态定义
  const selectedPosition = ref('TOP')
  const championList = ref<Champion[]>([])
  const filterForm = ref({
    tier: 'platinum_plus',
    mode: 'ranked'
  })
  
  // 获取英雄数据
  const fetchChampionData = async () => {
    try {
      const params = new URLSearchParams({
        region: 'kr',
        mode: filterForm.value.mode,
        tier: filterForm.value.tier
      })
  
      const response = await axios.post(
        '/api/match_data/tier_list',
        params,
        {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
          }
        }
      )
  
      if (response.data?.data?.[selectedPosition.value]) {
        championList.value = response.data.data[selectedPosition.value]
      }
    } catch (error) {
      ElMessage.error('获取英雄数据失败')
      console.error('获取英雄数据失败:', error)
    }
  }
  
  // 处理位置变更
  const handlePositionChange = () => {
    fetchChampionData()
  }
  
  // 监听筛选条件变化
  watch(filterForm, () => {
    fetchChampionData()
  }, { deep: true })
  
  onMounted(() => {
    fetchChampionData()
  })
  </script>
  
  <style scoped>
  .match-data {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
  }
  
  .position-selector {
    margin-bottom: 20px;
    text-align: center;
  }
  
  .filter-section {
    margin-bottom: 20px;
  }
  
  .champion-info {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  
  .champion-icon {
    width: 40px;
    height: 40px;
    border-radius: 50%;
  }
  
  .counter-champions {
    display: flex;
    gap: 8px;
  }
  
  .counter-icon {
    width: 24px;
    height: 24px;
    border-radius: 50%;
  }
  
  @media (max-width: 768px) {
    .match-data {
      padding: 10px;
    }
    
    .position-selector {
      overflow-x: auto;
    }
    
    :deep(.el-form--inline) {
      flex-wrap: wrap;
    }
    
    :deep(.el-form-item) {
      margin-right: 0;
      margin-bottom: 10px;
      width: 100%;
    }
  }
  </style>