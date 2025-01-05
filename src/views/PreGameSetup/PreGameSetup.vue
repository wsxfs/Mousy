<template>
  <div 
    class="pre-game-setup"
    @dragover.prevent="handleDragOver"
    @dragleave.prevent="handleDragLeave"
    @drop.prevent="handleDrop"
    :data-dragging="isDragging"
  >
    <div class="setup-header">
      <h2>赛前预设</h2>
    </div>
      
    <el-form :model="form" label-position="top" ref="formRef" class="setup-form">
      <el-row :gutter="20">
        <!-- 左侧列 -->
        <el-col :xs="24" :sm="12">
          <!-- 基础设置卡片 -->
          <el-card class="setting-card">
            <template #header>
              <div class="card-header">
                <span>基础设置</span>
              </div>
            </template>
            <div class="switch-group">
              <el-form-item label="自动接受对局" prop="auto_accept">
                <div class="switch-wrapper" :class="{ 'unsaved': isFieldChanged('auto_accept') }">
                  <el-switch v-model="form.auto_accept" class="custom-switch"></el-switch>
                </div>
              </el-form-item>
              
              <el-form-item label="自动接受交换位置" prop="auto_accept_swap_position">
                <div class="switch-wrapper" :class="{ 'unsaved': isFieldChanged('auto_accept_swap_position') }">
                  <el-switch v-model="form.auto_accept_swap_position" class="custom-switch" disabled></el-switch>
                  <el-tag size="small" type="warning" class="feature-tag">开发中</el-tag>
                </div>
              </el-form-item>
              
              <el-form-item label="自动接受交换英雄" prop="auto_accept_swap_champion">
                <div class="switch-wrapper" :class="{ 'unsaved': isFieldChanged('auto_accept_swap_champion') }">
                  <el-switch v-model="form.auto_accept_swap_champion" class="custom-switch" disabled></el-switch>
                  <el-tag size="small" type="warning" class="feature-tag">开发中</el-tag>
                </div>
              </el-form-item>
            </div>
          </el-card>

          <!-- 极地大乱斗设置卡片 -->
          <el-card class="setting-card">
            <template #header>
              <div class="card-header">
                <span>极地大乱斗 - 自动选择英雄</span>
                <div class="card-switch">
                  <el-switch 
                    v-model="form.aram_auto_pick_enabled" 
                    class="custom-switch"
                    :class="{ 'unsaved': isFieldChanged('aram_auto_pick_enabled') }"
                  ></el-switch>
                </div>
              </div>
            </template>
            
            <div class="aram-settings">
              <el-form-item prop="aram_auto_pick_delay">
                <div class="select-wrapper" :class="{ 'unsaved': isFieldChanged('aram_auto_pick_delay') }">
                  <div class="delay-input-group">
                    <span class="delay-label">等待时间(秒)</span>
                    <div class="slider-container">
                      <el-slider
                        v-model="form.aram_auto_pick_delay"
                        :min="0"
                        :max="5"
                        :step="0.1"
                        :format-tooltip="(val: number) => `${val}秒`"
                        :marks="{ 2.5: '读秒节点' }"
                        class="delay-slider"
                      />
                    </div>
                    <el-input-number 
                      v-model="form.aram_auto_pick_delay" 
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
              prop="aram_auto_pick_champions"
            >
              <div class="select-wrapper" :class="{ 'unsaved': isFieldChanged('aram_auto_pick_champions') }">
                <HeroSelector
                  v-model="form.aram_auto_pick_champions"
                  :heroes="heroes"
                  :getResourceUrl="getResourceUrl"
                />
              </div>
            </el-form-item>
          </el-card>
        </el-col>

        <!-- 右侧列 -->
        <el-col :xs="24" :sm="12">
          <!-- 经典模式选择设置卡片 -->
          <el-card class="setting-card">
            <template #header>
              <div class="card-header">
                <span>经典模式 - 自动选择英雄</span>
                <div class="card-switch">
                  <el-switch 
                    v-model="form.auto_pick_enabled" 
                    class="custom-switch"
                    :class="{ 'unsaved': isFieldChanged('auto_pick_enabled') }"
                  ></el-switch>
                </div>
              </div>
            </template>
            
            <div class="classic-pick-settings">
              <el-form-item prop="auto_pick_delay">
                <div class="select-wrapper" :class="{ 'unsaved': isFieldChanged('auto_pick_delay') }">
                  <div class="delay-input-group">
                    <span class="delay-label">等待时间(秒)</span>
                    <div class="slider-container">
                      <el-slider
                        v-model="form.auto_pick_delay"
                        :min="0"
                        :max="5"
                        :step="0.1"
                        :format-tooltip="(val: number) => `${val}秒`"
                        class="delay-slider"
                      />
                    </div>
                    <el-input-number 
                      v-model="form.auto_pick_delay" 
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
              prop="auto_pick_champions"
            >
              <div class="select-wrapper" :class="{ 'unsaved': isFieldChanged('auto_pick_champions') }">
                <HeroSelector
                  v-model="form.auto_pick_champions"
                  :heroes="heroes"
                  :getResourceUrl="getResourceUrl"
                />
              </div>
            </el-form-item>
          </el-card>

          <!-- 经典模式禁用设置卡片 -->
          <el-card class="setting-card">
            <template #header>
              <div class="card-header">
                <span>经典模式 - 自动禁用英雄</span>
                <div class="card-switch">
                  <el-switch 
                    v-model="form.auto_ban_enabled" 
                    class="custom-switch"
                    :class="{ 'unsaved': isFieldChanged('auto_ban_enabled') }"
                  ></el-switch>
                </div>
              </div>
            </template>
            
            <div class="classic-ban-settings">
              <el-form-item prop="auto_ban_delay">
                <div class="select-wrapper" :class="{ 'unsaved': isFieldChanged('auto_ban_delay') }">
                  <div class="delay-input-group">
                    <span class="delay-label">等待时间(秒)</span>
                    <div class="slider-container">
                      <el-slider
                        v-model="form.auto_ban_delay"
                        :min="0"
                        :max="5"
                        :step="0.1"
                        :format-tooltip="(val: number) => `${val}秒`"
                        class="delay-slider"
                      />
                    </div>
                    <el-input-number 
                      v-model="form.auto_ban_delay" 
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
              prop="auto_ban_champions"
            >
              <div class="select-wrapper" :class="{ 'unsaved': isFieldChanged('auto_ban_champions') }">
                <HeroSelector
                  v-model="form.auto_ban_champions"
                  :heroes="heroes"
                  :getResourceUrl="getResourceUrl"
                />
              </div>
            </el-form-item>
          </el-card>
        </el-col>
      </el-row>

      <!-- 底部操作按钮 -->
      <el-card class="setting-card action-card">
        <div class="form-actions">
          <div class="left-buttons">
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
      </el-card>
    </el-form>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import type { FormInstance } from 'element-plus'
import { saveAs } from 'file-saver'
import HeroSelector from '../../components/HeroSelector.vue'

// 定义接口
interface Hero {
  id: string
  name: string
  alias: string
  squarePortraitPath: string
}

interface FormState {
  auto_accept: boolean
  auto_pick_champions: string[]
  auto_ban_champions: string[]
  auto_accept_swap_position: boolean
  auto_accept_swap_champion: boolean
  aram_auto_pick_enabled: boolean
  aram_auto_pick_champions: string[]
  aram_auto_pick_delay: number
  auto_pick_enabled: boolean
  auto_pick_delay: number
  auto_ban_enabled: boolean
  auto_ban_delay: number
}

interface ResourceResponse {
  champion_icons?: Record<string, string>
}

// 表单引用
const formRef = ref<FormInstance>()

// 存储默认值
const defaultSettings = ref<FormState | null>(null)

// 表单数据
const form = reactive<FormState>({
  auto_accept: false,
  auto_pick_champions: [],
  auto_ban_champions: [],
  auto_accept_swap_position: false,
  auto_accept_swap_champion: false,
  aram_auto_pick_enabled: false,
  aram_auto_pick_champions: [],
  aram_auto_pick_delay: 0.0,
  auto_pick_enabled: false,
  auto_pick_delay: 0.0,
  auto_ban_enabled: false,
  auto_ban_delay: 0.0,
})

// 记录最后一次成功保存的状态
const lastSavedState = ref<FormState | null>(null)

// 计算是否有未保存的更改
const hasUnsavedChanges = computed(() => {
  if (!lastSavedState.value) return false
  return Object.keys(form).some((key) => 
    form[key as keyof FormState] !== lastSavedState.value?.[key as keyof FormState]
  )
})

// 获取默认设置
const fetchDefaultSettings = async (): Promise<void> => {
  try {
    const response = await axios.get<FormState>('/api/user_settings/get')
    defaultSettings.value = response.data
    // 初始化表单
    Object.assign(form, response.data)
    // 记录初始状态为已保存状态
    lastSavedState.value = { ...response.data }
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
      champion_icons: heroList.map(hero => hero.id)
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
        id,
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
    lastSavedState.value = { ...form }
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
    Object.assign(form, lastSavedState.value)
  }
}

// 检查特定字段是否有更改
const isFieldChanged = (fieldName: keyof FormState): boolean => {
  if (!lastSavedState.value) return false
  return form[fieldName] !== lastSavedState.value[fieldName]
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
const handleDragOver = (): void => {
  isDragging.value = true
}

// 处理拖拽离开
const handleDragLeave = (): void => {
  isDragging.value = false
}

// 修改处理拖拽放下
const handleDrop = async (event: DragEvent): Promise<void> => {
  isDragging.value = false  // 重置拖拽状态
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

onMounted(() => {
  fetchDefaultSettings()
  fetchHeroes()
})
</script>

<style scoped>
.pre-game-setup {
  max-width: 940px;
  margin: 0 auto;
  padding: 20px;
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
  margin-bottom: 24px;
}

.setup-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #303133;
}

.setup-form {
  background-color: #fff;
}

.switch-group {
  display: flex;
  flex-direction: row;
  gap: 24px;
  margin-bottom: 32px;
}

.custom-switch {
  margin-left: 8px;
}

.form-actions {
  margin-top: 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.left-buttons {
  display: flex;
  gap: 16px;
}

.right-buttons {
  margin-left: auto;
}

.save-button,
.reset-button {
  min-width: 90px;
  transition: all 0.3s ease;
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
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
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
  gap: 8px;
  padding: 4px 8px;
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
  width: 24px;
  height: 24px;
  border-radius: 4px;
}

.hero-search-container {
  display: flex;
  gap: 10px;
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
  gap: 16px;
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
}

.delay-slider {
  margin: 0;
}

.delay-input {
  width: 100px;
  flex-shrink: 0;
}

.feature-tag {
  margin-left: 8px;
  font-size: 12px;
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
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
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
}

.card-switch {
  display: flex;
  align-items: center;
}

.card-switch .custom-switch {
  margin-left: 12px;
}

.action-card {
  margin-top: 20px;
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
    padding: 10px;
  }
  
  .switch-group {
    gap: 16px;
    margin-bottom: 24px;
  }
  
  .switch-group :deep(.el-form-item) {
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .switch-group :deep(.el-form-item__content) {
    margin-left: 0 !important;
    flex: none !important;
  }

  .switch-group :deep(.el-form-item__label) {
    line-height: 32px;
    margin-right: 12px;
    flex: 1;
  }

  .custom-switch {
    margin-left: 0;
  }

  .form-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .left-buttons,
  .right-buttons {
    display: flex;
    flex-direction: column;
    gap: 10px;
    width: 100%;
  }

  .right-buttons {
    margin-top: 10px;
  }

  .switch-wrapper.unsaved::after {
    top: 50%;
    transform: translateY(-50%);
    right: -12px;
  }

  .switch-wrapper.unsaved {
    margin-right: 8px;
  }

  .select-wrapper.unsaved {
    width: calc(100% - 20px);
    margin-right: 20px;
  }

  .hero-search-container {
    flex-direction: column;
  }
  
  .selected-heroes,
  .hero-search {
    width: 100%;
  }

  .delay-input-group {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }
  
  .delay-label {
    min-width: unset;
    margin-bottom: 4px;
  }
  
  .slider-container {
    width: 100%;
    min-width: unset;
  }
  
  .delay-input {
    width: 100%;
  }

  .feature-tag {
    position: absolute;
    right: -70px;
    top: 50%;
    transform: translateY(-50%);
  }

  .card-header {
    font-size: 14px;
  }
  
  .card-switch .custom-switch {
    margin-left: 8px;
  }

  .setting-card {
    margin-bottom: 16px;
  }
}
</style>