<template>
  <div 
    class="pre-game-setup"
    @dragover.prevent="handleDragOver"
    @dragleave.prevent="handleDragLeave"
    @drop.prevent="handleDrop"
    :data-dragging="isDragging"
  >
    <div class="setup-header">
      <div class="header-content">
        <h2 class="setup-title">赛前预设</h2>
        <div class="basic-settings">
          <div class="switch-group">
            <div 
              class="light-button" 
              :class="{ 
                'is-active': form.auto_accept,
                'unsaved': isFieldChanged('auto_accept')
              }"
              @click="form.auto_accept = !form.auto_accept"
            >
              <div class="light-indicator"></div>
              <span class="button-text">自动接受对局</span>
            </div>

            <div 
              class="light-button" 
              :class="{ 
                'is-active': false,
                'unsaved': false,
                'is-disabled': true
              }"
              @click="() => {}"
            >
              <div class="light-indicator"></div>
              <span class="button-text">自动接受交换位置</span>
              <el-tag size="small" type="warning" class="feature-tag">开发中</el-tag>
            </div>

            <div 
              class="light-button" 
              :class="{ 
                'is-active': false,
                'unsaved': false,
                'is-disabled': true
              }"
              @click="() => {}"
            >
              <div class="light-indicator"></div>
              <span class="button-text">自动接受交换英雄</span>
              <el-tag size="small" type="warning" class="feature-tag">开发中</el-tag>
            </div>
          </div>
        </div>
      </div>
    </div>
      
    <el-form :model="form" label-position="top" ref="formRef" class="setup-form">
      <!-- 添加可排序容器 -->
      <div ref="sortableContainer">
        <template v-for="rowType in cardOrder" :key="rowType">
          <el-row :gutter="20" class="draggable-row" :class="rowType">
            <!-- 拖动手柄 -->
            <div class="drag-handle">
              <div class="drag-lines">
                <span></span>
                <span></span>
                <span></span>
              </div>
              <div class="drag-label">{{ rowType === 'ranked' ? '排位' : '匹配' }}</div>
            </div>
            
            <!-- 其他行内容保持不变 -->
            <template v-if="rowType === 'ranked'">
              <el-col :xs="24" :sm="12">
                <el-card class="setting-card">
                  <template #header>
                    <div class="card-header">
                      <span>排位模式 - 自动选择英雄</span>
                      <div class="card-switch">
                        <el-switch 
                          v-model="form.ranked.pick.enabled" 
                          class="custom-switch"
                          :class="{ 'unsaved': isFieldChanged('ranked.pick.enabled') }"
                        ></el-switch>
                      </div>
                    </div>
                  </template>
                  
                  <div class="classic-pick-settings" :class="{ 'card-disabled': !form.ranked.pick.enabled }">
                    <el-form-item prop="ranked.pick.delay">
                      <div class="select-wrapper" :class="{ 'unsaved': isFieldChanged('ranked.pick.delay') }">
                        <div class="delay-input-group">
                          <span class="delay-label">等待时间(秒)</span>
                          <div class="slider-container">
                            <el-slider
                              v-model="form.ranked.pick.delay"
                              :min="0"
                              :max="20"
                              :step="0.1"
                              :format-tooltip="(val: number) => `${val}秒`"
                              class="delay-slider"
                            />
                          </div>
                          <el-input-number 
                            v-model="form.ranked.pick.delay" 
                            :min="0"
                            :max="20"
                            :step="0.1"
                            :precision="1"
                            controls-position="right"
                            class="delay-input"
                          />
                        </div>
                      </div>
                    </el-form-item>
                  </div>

                  <el-form-item 
                    v-for="position in positions"
                    :key="position.key"
                    :prop="`ranked.pick.champions.${position.key}`"
                  >
                    <div class="position-select-wrapper">
                      <div class="position-label">
                        <span class="position-name">{{ position.name }}</span>
                      </div>
                      <div class="select-wrapper" :class="{ 'unsaved': isFieldChanged(`ranked.pick.champions.${position.key}`) }">
                        <HeroSelector
                          v-model="form.ranked.pick.champions[position.key]"
                          :heroes="heroes"
                          :getResourceUrl="getResourceUrl"
                          :previewCount="5"
                        />
                      </div>
                    </div>
                  </el-form-item>
                </el-card>
              </el-col>

              <el-col :xs="24" :sm="12">
                <el-card class="setting-card">
                  <template #header>
                    <div class="card-header">
                      <span>排位模式 - 自动禁用英雄</span>
                      <div class="card-switch">
                        <el-switch 
                          v-model="form.ranked.ban.enabled" 
                          class="custom-switch"
                          :class="{ 'unsaved': isFieldChanged('ranked.ban.enabled') }"
                        ></el-switch>
                      </div>
                    </div>
                  </template>
                  
                  <div class="classic-ban-settings" :class="{ 'card-disabled': !form.ranked.ban.enabled }">
                    <el-form-item prop="ranked.ban.delay">
                      <div class="select-wrapper" :class="{ 'unsaved': isFieldChanged('ranked.ban.delay') }">
                        <div class="delay-input-group">
                          <span class="delay-label">等待时间(秒)</span>
                          <div class="slider-container">
                            <el-slider
                              v-model="form.ranked.ban.delay"
                              :min="0"
                              :max="20"
                              :step="0.1"
                              :format-tooltip="(val: number) => `${val}秒`"
                              class="delay-slider"
                            />
                          </div>
                          <el-input-number 
                            v-model="form.ranked.ban.delay" 
                            :min="0"
                            :max="20"
                            :step="0.1"
                            :precision="1"
                            controls-position="right"
                            class="delay-input"
                          />
                        </div>
                      </div>
                    </el-form-item>
                  </div>

                  <el-form-item 
                    v-for="position in positions"
                    :key="position.key"
                    :prop="`ranked.ban.champions.${position.key}`"
                  >
                    <div class="position-select-wrapper">
                      <div class="position-label">
                        <span class="position-name">{{ position.name }}</span>
                      </div>
                      <div class="select-wrapper" :class="{ 'unsaved': isFieldChanged(`ranked.ban.champions.${position.key}`) }">
                        <HeroSelector
                          v-model="form.ranked.ban.champions[position.key]"
                          :heroes="heroes"
                          :getResourceUrl="getResourceUrl"
                          :previewCount="5"
                        />
                      </div>
                    </div>
                  </el-form-item>
                </el-card>
              </el-col>
            </template>
            
            <!-- 匹配/大乱斗行 -->
            <template v-else>
              <el-col :xs="24" :sm="12">
                <el-card class="setting-card">
                  <template #header>
                    <div class="card-header">
                      <span>匹配模式 - 自动选择英雄</span>
                      <div class="card-switch">
                        <el-switch 
                          v-model="form.normal.pick.enabled" 
                          class="custom-switch"
                          :class="{ 'unsaved': isFieldChanged('normal.pick.enabled') }"
                        ></el-switch>
                      </div>
                    </div>
                  </template>
                  
                  <div class="classic-pick-settings" :class="{ 'card-disabled': !form.normal.pick.enabled }">
                    <el-form-item prop="normal.pick.delay">
                      <div class="select-wrapper" :class="{ 'unsaved': isFieldChanged('normal.pick.delay') }">
                        <div class="delay-input-group">
                          <span class="delay-label">等待时间(秒)</span>
                          <div class="slider-container">
                            <el-slider
                              v-model="form.normal.pick.delay"
                              :min="0"
                              :max="5"
                              :step="0.1"
                              :format-tooltip="(val: number) => `${val}秒`"
                              class="delay-slider"
                            />
                          </div>
                          <el-input-number 
                            v-model="form.normal.pick.delay" 
                            :min="0"
                            :max="5"
                            :step="0.1"
                            :precision="1"
                            controls-position="right"
                            class="delay-input"
                          />
                        </div>
                      </div>
                    </el-form-item>
                  </div>

                  <el-form-item 
                    prop="normal.pick.champions"
                  >
                    <div class="select-wrapper" :class="{ 'unsaved': isFieldChanged('normal.pick.champions') }">
                      <HeroSelector
                        v-model="form.normal.pick.champions"
                        :heroes="heroes"
                        :getResourceUrl="getResourceUrl"
                        :previewCount="6"
                      />
                    </div>
                  </el-form-item>
                </el-card>
              </el-col>

              <el-col :xs="24" :sm="12">
                <el-card class="setting-card">
                  <template #header>
                    <div class="card-header">
                      <span>极地大乱斗 - 自动选择英雄</span>
                      <div class="card-switch">
                        <el-switch 
                          v-model="form.aram.pick.enabled" 
                          class="custom-switch"
                          :class="{ 'unsaved': isFieldChanged('aram.pick.enabled') }"
                        ></el-switch>
                      </div>
                    </div>
                  </template>
                  
                  <div class="aram-settings" :class="{ 'card-disabled': !form.aram.pick.enabled }">
                    <el-form-item prop="aram.pick.delay">
                      <div class="select-wrapper" :class="{ 'unsaved': isFieldChanged('aram.pick.delay') }">
                        <div class="delay-input-group">
                          <span class="delay-label">等待时间(秒)</span>
                          <div class="slider-container">
                            <el-slider
                              v-model="form.aram.pick.delay"
                              :min="0"
                              :max="5"
                              :step="0.1"
                              :format-tooltip="(val: number) => `${val}秒`"
                              :marks="{ 2.5: '读秒节点' }"
                              class="delay-slider"
                            />
                          </div>
                          <el-input-number 
                            v-model="form.aram.pick.delay" 
                            :min="0"
                            :max="5"
                            :step="0.1"
                            :precision="1"
                            controls-position="right"
                            class="delay-input"
                          />
                        </div>
                      </div>
                    </el-form-item>
                  </div>

                  <el-form-item 
                    prop="aram.pick.champions"
                  >
                    <div class="select-wrapper" :class="{ 'unsaved': isFieldChanged('aram.pick.champions') }">
                      <HeroSelector
                        v-model="form.aram.pick.champions"
                        :heroes="heroes"
                        :getResourceUrl="getResourceUrl"
                        :previewCount="6"
                      />
                    </div>
                  </el-form-item>
                </el-card>
              </el-col>
            </template>
          </el-row>
        </template>
      </div>

      <!-- 底部操作按钮 -->
      <el-card class="setting-card action-card">
        <div class="form-actions">
          <div class="action-button-group">
            <!-- 主要操作按钮 -->
            <div class="primary-actions">
              <el-button 
                :type="hasUnsavedChanges ? 'warning' : 'primary'"
                @click="onSubmit()"
                class="save-button"
              >
                <transition name="fade" mode="out-in">
                  <span :key="hasUnsavedChanges ? 'unsaved' : 'saved'">
                    {{ hasUnsavedChanges ? '保存更改' : '已保存' }}
                  </span>
                </transition>
              </el-button>
              <el-button 
                @click="onReset()"
                :disabled="!hasUnsavedChanges"
                class="reset-button"
              >重置</el-button>
            </div>
            
            <!-- 导入导出按钮 -->
            <div class="secondary-actions">
              <el-button 
                @click="onImportSettings"
                class="import-button"
              >导入设置</el-button>
              <el-button 
                @click="onExportSettings"
                class="export-button"
                draggable="true"
                @dragstart="handleExportDragStart"
              >导出设置</el-button>
            </div>
          </div>
        </div>
      </el-card>
    </el-form>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted, computed, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import type { FormInstance } from 'element-plus'
import { saveAs } from 'file-saver'
import HeroSelector from '../../components/HeroSelector.vue'
import Sortable from 'sortablejs'
import type { Hero, FormState, FormPath, PositionKey, ResourceResponse } from './types'

// 表单引用
const formRef = ref<FormInstance>()

// 存储默认值
const defaultSettings = ref<FormState | null>(null)

// 表单数据
const form = reactive<FormState>({
  // 基础设置
  auto_accept: false,
  auto_accept_swap_position: false,
  auto_accept_swap_champion: false,

  // 布局设置
  layout: {
    card_order: ['ranked', 'normal']
  },

  // 游戏模式设置
  ranked: {
    pick: {
      enabled: false,
      delay: 0.0,
      champions: {
        top: [],
        jungle: [],
        middle: [],
        bottom: [],
        support: []
      }
    },
    ban: {
      enabled: false,
      delay: 0.0,
      champions: {
        top: [],
        jungle: [],
        middle: [],
        bottom: [],
        support: []
      }
    }
  },
  normal: {
    pick: {
      enabled: false,
      delay: 0.0,
      champions: []
    },
    ban: {
      enabled: false,
      delay: 0.0,
      champions: []
    }
  },
  aram: {
    pick: {
      enabled: false,
      delay: 0.0,
      champions: []
    }
  }
})

// 记录最后一次成功保存的状态
const lastSavedState = ref<FormState | null>(null)

// 计算是否有未保存的更改
const hasUnsavedChanges = computed(() => {
  if (!lastSavedState.value) return false

  // 递归比较对象
  const isObjectChanged = (current: any, saved: any): boolean => {
    if (current === saved) return false
    
    if (typeof current !== 'object' || current === null ||
        typeof saved !== 'object' || saved === null) {
      return current !== saved
    }
    
    const currentKeys = Object.keys(current)
    const savedKeys = Object.keys(saved)
    
    if (currentKeys.length !== savedKeys.length) return true
    
    return currentKeys.some(key => isObjectChanged(current[key], saved[key]))
  }

  return isObjectChanged(form, lastSavedState.value)
})

// 添加深拷贝函数
const deepClone = <T>(obj: T): T => {
  if (obj === null || typeof obj !== 'object') {
    return obj
  }
  
  if (Array.isArray(obj)) {
    return obj.map(item => deepClone(item)) as unknown as T
  }
  
  const cloned = {} as T
  Object.keys(obj as object).forEach(key => {
    cloned[key as keyof T] = deepClone((obj as any)[key])
  })
  return cloned
}

// 修改 fetchDefaultSettings 函数中的保存状态部分
const fetchDefaultSettings = async (): Promise<void> => {
  try {
    const response = await axios.get<FormState>('/api/user_settings/get')
    defaultSettings.value = deepClone(response.data)
    // 初始化表单
    Object.assign(form, response.data)
    // 记录初始状态为已保存状态
    lastSavedState.value = deepClone(form)
  } catch (error) {
    ElMessage({
      message: '获取默认设置失败',
      type: 'error'
    })
    console.error('Error fetching default settings:', error)
  }
}

// 添加英雄列表状态
const heroes = ref<Hero[]>([])

// 添加资源URL的引用
const gameResources = ref<ResourceResponse>({})

// 添加获取资源URL的方法
const getResourceUrl = (
  type: keyof ResourceResponse, 
  id: string | number
): string => {
  const resources = gameResources.value[type] as Record<string | number, string>
  if (resources?.[id]) {
    return `data:image/png;base64,${resources[id]}`
  }
  return '/placeholder.png'
}

// 添加加载英雄图标的方法
const loadChampionIcons = async (heroList: Hero[]) => {
  try {
    const resourceRequest = {
      champion_icons: heroList.map(hero => hero.id.toString())
    }
    
    const response = await axios.post<ResourceResponse>(
      '/api/common/game_resource/batch_get_resources',
      resourceRequest
    )
    
    gameResources.value = response.data
  } catch (error) {
    console.error('加载英雄图标失败:', error)
    ElMessage.error('加载英雄图标失败')
  }
}

// 修改 fetchHeroes 方法，在获取英雄列表后加载图标
const fetchHeroes = async () => {
  try {
    const response = await axios.get('/api/common/game_resource/champions_info')
    const heroesData = response.data
    heroes.value = Object.entries(heroesData)
      .filter(([id]) => id !== '-1')
      .map(([id, data]: [string, any]) => ({
        id: parseInt(id),
        name: data.name,
        alias: data.alias,
        squarePortraitPath: data.squarePortraitPath
      }))
    
    // 加载英图标
    await loadChampionIcons(heroes.value)
  } catch (error) {
    ElMessage({
      message: '获取英雄数据失败',
      type: 'error'
    })
    console.error('Error fetching heroes:', error)
  }
}

// 提交表单
const onSubmit = async (): Promise<void> => {
  try {
    const response = await axios.post('/api/user_settings/update_all', form)
    lastSavedState.value = deepClone(form)
    ElMessage({
      message: '设置已保存！',
      type: 'success'
    })
    console.log('Response from server:', response.data)
  } catch (error) {
    ElMessage({
      message: '保存失败，请稍后试。',
      type: 'error'
    })
    console.error('Error sending settings to server:', error)
  }
}

// 重置表单
const onReset = (): void => {
  if (lastSavedState.value) {
    Object.assign(form, deepClone(lastSavedState.value))
  }
}

// 检查特定字段是否有更改
const isFieldChanged = (path: FormPath): boolean => {
  if (!lastSavedState.value) return false
  
  // 处理嵌套路径
  const getNestedValue = (obj: any, path: string): any => {
    return path.split('.').reduce((prev, curr) => {
      return prev?.[curr]
    }, obj)
  }
  
  const currentValue = getNestedValue(form, path)
  const savedValue = getNestedValue(lastSavedState.value, path)
  
  // 处理数组类型
  if (Array.isArray(currentValue) && Array.isArray(savedValue)) {
    if (currentValue.length !== savedValue.length) return true
    return JSON.stringify(currentValue) !== JSON.stringify(savedValue)
  }
  
  // 处理对象类型
  if (typeof currentValue === 'object' && currentValue !== null &&
      typeof savedValue === 'object' && savedValue !== null) {
    return JSON.stringify(currentValue) !== JSON.stringify(savedValue)
  }
  
  // 处理基本类型
  return currentValue !== savedValue
}

// 导入设置
const onImportSettings = async (): Promise<void> => {
  try {
    const fileInput = document.createElement('input')
    fileInput.type = 'file'
    fileInput.accept = '.json'
    fileInput.onchange = async (event: Event) => {
      const file = (event.target as HTMLInputElement).files?.[0]
      if (file) {
        const text = await file.text()
        const importedSettings = JSON.parse(text)
        Object.assign(form, importedSettings)
        ElMessage({
          message: '设置已导入！',
          type: 'success'
        })
      }
    }
    fileInput.click()
  } catch (error) {
    ElMessage({
      message: '导入失败，请重试。',
      type: 'error'
    })
  }
}

// 导出设置
const onExportSettings = (): void => {
  const blob = new Blob([JSON.stringify(form)], { type: 'application/json' })
  saveAs(blob, 'settings.json')
  ElMessage({
    message: '设置已导出！',
    type: 'success'
  })
}

// 添加拖拽状态
const isDragging = ref(false)

// 处理拖拽悬停
const handleDragOver = (event: DragEvent) => {
  // 检查是否是文件拖拽
  if (!event.dataTransfer?.types.includes('Files')) return
  
  event.preventDefault()
  isDragging.value = true
}

// 处理拖拽离开
const handleDragLeave = (event: DragEvent) => {
  // 检查是否是文件拖拽
  if (!event.dataTransfer?.types.includes('Files')) return
  
  event.preventDefault()
  isDragging.value = false
}

// 修改处理拖拽放下
const handleDrop = async (event: DragEvent) => {
  // 检查是否是文件拖拽
  if (!event.dataTransfer?.types.includes('Files')) return
  
  event.preventDefault()
  isDragging.value = false
  
  try {
    const file = event.dataTransfer?.files[0]
    if (!file || !file.name.endsWith('.json')) {
      ElMessage({
        message: '请拖入有效的 JSON 设置文件',
        type: 'warning'
      })
      return
    }

    const text = await file.text()
    const importedSettings = JSON.parse(text)
    Object.assign(form, importedSettings)
    ElMessage({
      message: '设置已导入！',
      type: 'success'
    })
  } catch (error) {
    ElMessage({
      message: '导入失败，请确保文件格式正确',
      type: 'error'
    })
  }
}

// 添加导出拖拽处理函数
const handleExportDragStart = (event: DragEvent): void => {
  if (!event.dataTransfer) return

  // 创建包含设置的Blob
  const settingsBlob = new Blob([JSON.stringify(form, null, 2)], { 
    type: 'application/json' 
  })
  
  // 创建文件对象
  const file = new File([settingsBlob], 'settings.json', { 
    type: 'application/json' 
  })

  // 设置多种数据格式以提高兼容性
  event.dataTransfer.setData('text/plain', JSON.stringify(form, null, 2))
  event.dataTransfer.setData('application/json', JSON.stringify(form, null, 2))
  
  // 添加文件对象
  try {
    event.dataTransfer.setData('DownloadURL', `application/json:settings.json:${URL.createObjectURL(file)}`)
    event.dataTransfer.setData('text/uri-list', URL.createObjectURL(file))
    
    // 如果浏览器支持 DataTransferItemList
    if (event.dataTransfer.items) {
      event.dataTransfer.items.add(file)
    }
  } catch (error) {
    console.warn('Drag and drop file creation not fully supported:', error)
  }

  event.dataTransfer.effectAllowed = 'copyMove'
}

const positions: Array<{ key: PositionKey; name: string }> = [
  { key: 'top', name: '上单' },
  { key: 'jungle', name: '打野' },
  { key: 'middle', name: '中单' },
  { key: 'bottom', name: '下路' },
  { key: 'support', name: '辅助' }
]

// 将 cardOrder ref 替换为 computed
const cardOrder = computed({
  get: () => form.layout.card_order,
  set: (newOrder) => {
    form.layout.card_order = newOrder
  }
})

// 添加一个 ref 来引用可排序的容器
const sortableContainer = ref<HTMLElement | null>(null)

// 修改 onMounted 钩子
onMounted(() => {
  fetchDefaultSettings()
  fetchHeroes()
  
  nextTick(() => {
    if (sortableContainer.value) {
      Sortable.create(sortableContainer.value, {
        animation: 150,
        handle: '.drag-handle',
        ghostClass: 'sortable-ghost',
        chosenClass: 'sortable-chosen',
        dragClass: 'sortable-drag',
        onEnd: ({ oldIndex, newIndex }) => {
          if (oldIndex !== undefined && newIndex !== undefined) {
            const newOrder = [...form.layout.card_order]
            const [movedItem] = newOrder.splice(oldIndex, 1)
            newOrder.splice(newIndex, 0, movedItem)
            form.layout.card_order = newOrder
          }
        }
      })
    }
  })
})
</script>

<style scoped>
.pre-game-setup {
  max-width: 940px;
  margin: 0 auto;
  padding: 12px;
  position: relative;
  min-height: 200px;
  border: 2px dashed transparent;
  transition: all 0.3s ease;
}

.pre-game-setup[data-dragging="true"] {
  border-color: var(--el-color-primary);
  background-color: rgba(var(--el-color-primary-rgb), 0.05);
}

.pre-game-setup::after {
  content: '拖拽设置文件到此处导入';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  font-size: 1.2em;
  color: #909399;
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s;
}

.pre-game-setup[data-dragging="true"]::after {
  opacity: 0.7;
}

.setup-header {
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;
}

.header-content h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #303133;
  white-space: nowrap;
}

.basic-settings {
  flex: 1;
}

.switch-group {
  display: flex;
  gap: 16px;
  justify-content: flex-end;
  padding: 8px 0;
}

.switch-group :deep(.el-form-item) {
  margin-bottom: 0;
}

.switch-group :deep(.el-form-item__label) {
  font-size: 14px;
  color: var(--el-text-color-regular);
  line-height: 1.2;
}

.switch-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  white-space: nowrap;
}

.light-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  background-color: var(--el-fill-color-light);
  cursor: pointer;
  transition: all 0.3s ease;
  border: 1px solid var(--el-border-color);
  position: relative;
}

.light-indicator {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: var(--el-text-color-disabled);
  transition: all 0.3s ease;
  box-shadow: 0 0 0 0 rgba(var(--el-color-primary-rgb), 0.4);
  flex-shrink: 0;
}

.button-text {
  font-size: 13px;
  color: var(--el-text-color-regular);
  transition: all 0.3s ease;
  white-space: nowrap;
}

/* 激活状态 */
.light-button.is-active {
  background-color: var(--el-color-primary-light-9);
  border-color: var(--el-color-primary);
}

.light-button.is-active .light-indicator {
  background-color: var(--el-color-primary);
  box-shadow: 0 0 0 3px rgba(var(--el-color-primary-rgb), 0.2);
  animation: glow 1.5s infinite;
}

.light-button.is-active .button-text {
  color: var(--el-color-primary);
  font-weight: 500;
}

/* 禁用状态 */
.light-button.is-disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 未保存状态 */
.light-button.unsaved::after {
  content: '';
  position: absolute;
  top: -4px;
  right: -4px;
  width: 8px;
  height: 8px;
  background-color: var(--el-color-warning);
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

/* 悬停效果 */
.light-button:not(.is-disabled):hover {
  background-color: var(--el-fill-color-darker);
}

.light-button.is-active:not(.is-disabled):hover {
  background-color: var(--el-color-primary-light-8);
}

@keyframes glow {
  0% {
    box-shadow: 0 0 0 0 rgba(var(--el-color-primary-rgb), 0.4);
  }
  50% {
    box-shadow: 0 0 0 4px rgba(var(--el-color-primary-rgb), 0.1);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(var(--el-color-primary-rgb), 0.4);
  }
}

@media (max-width: 768px) {
  .light-button {
    padding: 6px 12px;
  }

  .light-indicator {
    width: 6px;
    height: 6px;
  }

  .button-text {
    font-size: 12px;
  }
}

.form-actions {
  display: flex;
  justify-content: center;
  padding: 12px 0;
}

.action-button-group {
  display: flex;
  gap: 12px;
  align-items: center;
  flex-wrap: wrap;
  justify-content: center;
  max-width: 800px;
  width: 100%;
  padding: 4px 0;
}

.primary-actions,
.secondary-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.save-button,
.reset-button,
.import-button,
.export-button {
  min-width: 100px;
  transition: all 0.3s ease;
}

.save-button {
  position: relative;
  overflow: hidden;
}

.save-button::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(45deg, transparent, rgba(255,255,255,0.1), transparent);
  transform: translateX(-100%);
}

.save-button:hover::after {
  transform: translateX(100%);
  transition: transform 0.6s ease;
}

.switch-wrapper {
  position: relative;
  transition: all 0.3s ease;
}

.switch-wrapper.unsaved::after {
  content: '';
  position: absolute;
  top: -4px;
  right: -4px;
  width: 8px;
  height: 8px;
  background-color: var(--el-color-warning);
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0% {
    transform: scale(1);
    opacity: 1;
  }
  50% {
    transform: scale(1.2);
    opacity: 0.8;
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(2px);
}

.select-wrapper {
  position: relative;
  transition: all 0.3s ease;
  width: 100%;
}

.select-wrapper.unsaved::after {
  content: '';
  position: absolute;
  top: 50%;
  right: -12px;
  transform: translateY(-50%);
  width: 8px;
  height: 8px;
  background-color: var(--el-color-warning);
  border-radius: 50%;
  animation: pulse 1.5s infinite;
}

.hero-option {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 3px 6px;
  position: relative;
  cursor: pointer;
  width: 100%;
  font-weight: normal;
}

.hero-selected {
  color: var(--el-color-primary);
  font-weight: normal;
}

.check-icon {
  margin-left: auto;
  color: var(--el-color-primary);
  font-size: 16px;
}

.hero-icon {
  width: 20px;
  height: 20px;
  border-radius: 4px;
}

.hero-search-container {
  display: flex;
  gap: 6px;
  width: 100%;
}

.selected-heroes {
  flex: 2;
}

.hero-search {
  flex: 1;
  min-width: 200px;
}

.delay-input-group {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
}

.delay-label {
  min-width: 85px;
  color: var(--el-text-color-regular);
  font-size: 14px;
}

.slider-container {
  flex: 1;
  min-width: 150px;
  margin: 2px 0;
}

.delay-slider {
  margin: 4px 0;
  height: 4px;
}

.delay-input {
  width: 100px;
  flex-shrink: 0;
}

.feature-tag {
  margin-left: 4px;
  font-size: 11px;
  padding: 0 4px;
  height: 18px;
  line-height: 16px;
}

.export-button {
  cursor: move;
}

.export-button:hover {
  opacity: 0.9;
}

.export-button:active {
  cursor: grabbing;
}

.setting-card {
  margin-bottom: 8px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
  height: auto;
  min-height: 160px;
}

.setting-card:last-child {
  margin-bottom: 0;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 16px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  height: 20px;
  line-height: 20px;
}

:deep(.el-card__header) {
  padding: 6px 12px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.card-switch {
  display: flex;
  align-items: center;
  height: 100%;
}

.card-switch .custom-switch {
  margin-left: 12px;
}

.action-card {
  margin-top: 12px;
  background-color: transparent;
  border: none;
  box-shadow: none;
}

.action-card :deep(.el-card__body) {
  padding: 0;
}

:deep(.el-slider__marks-text) {
  color: var(--el-color-primary);
  font-weight: bold;
  font-size: 12px;
  margin-top: 4px;
}

:deep(.el-slider__stop) {
  width: 2px;
  height: 2px;
}

:deep(.el-slider__stop[style*="left: 50%"]) {
  width: 4px;
  height: 12px;
  background-color: var(--el-color-primary);
  border-radius: 2px;
  transform: translateY(-4px);
}

@media (max-width: 768px) {
  .pre-game-setup {
    padding: 6px;
  }
  
  .switch-group {
    flex-direction: column;
    gap: 8px;
    align-items: stretch;
  }
  
  .light-button {
    padding: 6px 12px;
  }

  .button-text {
    font-size: 12px;
  }

  .feature-tag {
    position: absolute;
    right: 8px;
    top: 50%;
    transform: translateY(-50%);
  }
}

.card-disabled {
  position: relative;
  opacity: 0.75;
  transition: opacity 0.3s ease;
}

.card-disabled::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.02);
  pointer-events: none;
  border-radius: 4px;
}

.card-disabled :deep(.el-input),
.card-disabled :deep(.el-slider),
.card-disabled :deep(.el-input-number) {
  opacity: 0.9;
}

.card-disabled:hover {
  opacity: 0.85;
}

.card-disabled :deep(.el-slider__runway) {
  background-color: var(--el-border-color-lighter);
}

.card-disabled :deep(.el-slider__bar) {
  background-color: var(--el-color-primary-light-5);
}

.card-disabled :deep(.el-input__inner),
.card-disabled :deep(.el-input-number__decrease),
.card-disabled :deep(.el-input-number__increase) {
  border-color: var(--el-border-color-lighter);
  background-color: var(--el-fill-color-lighter);
}

.classic-mode-container,
.flip-container,
.flipper,
.front,
.back {
  position: static;
  transform: none;
  backface-visibility: visible;
}

.mode-switch {
  display: none;
}

.el-row {
  margin-bottom: 12px;
}

@media (max-width: 768px) {
  .el-col {
    margin-bottom: 6px;
  }
  
  .el-row {
    margin-bottom: 6px;
  }
}

.position-select-wrapper {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
}

.position-label {
  flex-shrink: 0;
}

.position-name {
  font-size: 14px;
  color: var(--el-text-color-regular);
}

@media (max-width: 768px) {
  .position-select-wrapper {
    flex-direction: row;
    align-items: center;
    gap: 8px;
  }

  .position-label {
    min-width: 45px;
  }

  .position-name {
    font-size: 13px;
  }
}

.setting-card :deep(.el-form-item) {
  margin-bottom: 8px;
}

.draggable-row {
  position: relative;
  margin-bottom: 8px;
  transition: all 0.3s ease;
  padding: 12px;
  border-radius: 8px;
  border: 1px solid var(--el-border-color-lighter);
}

/* 排位模式样式 */
.draggable-row.ranked {
  background-color: rgba(var(--el-color-primary-rgb), 0.05);
  border-left: 4px solid var(--el-color-primary);
}

/* 匹配模式样式 */
.draggable-row.normal {
  background-color: rgba(var(--el-color-success-rgb), 0.05);
  border-left: 4px solid var(--el-color-success);
}

.drag-handle {
  position: absolute;
  left: -24px;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 60px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  cursor: move;
  opacity: 0.6;
  transition: opacity 0.2s ease;
  background-color: var(--el-fill-color-light);
  border-radius: 4px 0 0 4px;
  border: 1px solid var(--el-border-color-lighter);
  border-right: none;
}

.drag-handle:hover {
  opacity: 1;
}

.drag-lines {
  display: flex;
  flex-direction: column;
  gap: 3px;
  padding: 2px;
}

.drag-lines span {
  width: 12px;
  height: 1.5px;
  background-color: var(--el-text-color-regular);
  border-radius: 1px;
  display: block;
}

.drag-label {
  font-size: 12px;
  color: var(--el-text-color-regular);
  writing-mode: vertical-lr;
  letter-spacing: 1px;
}

/* 拖动时的样式 */
.sortable-ghost {
  opacity: 0.8;
}

.sortable-ghost.ranked {
  background-color: rgba(var(--el-color-primary-rgb), 0.1);
  border: 1px dashed var(--el-color-primary);
}

.sortable-ghost.normal {
  background-color: rgba(var(--el-color-success-rgb), 0.1);
  border: 1px dashed var(--el-color-success);
}

.sortable-chosen {
  transform: scale(1.01);
}

.sortable-drag {
  opacity: 0.9;
}

@media (max-width: 768px) {
  .draggable-row {
    padding: 8px;
    margin-bottom: 6px;
  }

  .drag-handle {
    left: -20px;
    width: 20px;
    height: 50px;
  }

  .drag-lines span {
    width: 10px;
  }

  .drag-label {
    font-size: 11px;
  }
}

.setting-card {
  margin-bottom: 20px;
}

:deep(.el-radio-button__inner) {
  padding: 8px 15px;
}

:deep(.el-radio-button:first-child .el-radio-button__inner) {
  border-radius: 4px 0 0 4px;
}

:deep(.el-radio-button:last-child .el-radio-button__inner) {
  border-radius: 0 4px 4px 0;
}

.setup-title {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 500;
  color: var(--el-text-color-primary);
  position: relative;
  padding-left: 12px;
  letter-spacing: 0.5px;
}

.setup-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 60%;
  transform: translateY(-50%);
  width: 3px;
  height: 25px;
  background: var(--el-color-primary);
  border-radius: 2px;
}
</style>