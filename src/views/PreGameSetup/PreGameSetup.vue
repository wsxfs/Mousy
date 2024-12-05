<template>
  <div class="pre-game-setup">
    <div class="setup-header">
      <h2>赛前预设</h2>
    </div>
      
    <el-form :model="form" label-position="top" ref="formRef" class="setup-form">
      <el-row :gutter="20">
        <!-- 开关类选项放在一列 -->
        <el-col :xs="24" :sm="10">
          <div class="switch-group">
            <el-form-item label="自动接受对局" prop="auto_accept">
              <div class="switch-wrapper" :class="{ 'unsaved': isFieldChanged('auto_accept') }">
                <el-switch v-model="form.auto_accept" class="custom-switch"></el-switch>
              </div>
            </el-form-item>
            
            <el-form-item label="自动接受交换位置" prop="auto_accept_swap_position">
              <div class="switch-wrapper" :class="{ 'unsaved': isFieldChanged('auto_accept_swap_position') }">
                <el-switch v-model="form.auto_accept_swap_position" class="custom-switch"></el-switch>
              </div>
            </el-form-item>
            
            <el-form-item label="自动接受交换英雄" prop="auto_accept_swap_champion">
              <div class="switch-wrapper" :class="{ 'unsaved': isFieldChanged('auto_accept_swap_champion') }">
                <el-switch v-model="form.auto_accept_swap_champion" class="custom-switch"></el-switch>
              </div>
            </el-form-item>
          </div>
        </el-col>

        <!-- 选择类选项放在另一列 -->
        <el-col :xs="24" :sm="14">
          <div class="aram-settings">
            <el-form-item label="启用极地大乱斗自动选择" prop="aram_auto_pick_enabled">
              <div class="switch-wrapper" :class="{ 'unsaved': isFieldChanged('aram_auto_pick_enabled') }">
                <el-switch v-model="form.aram_auto_pick_enabled" class="custom-switch"></el-switch>
              </div>
            </el-form-item>

            <el-form-item 
              label="等待时间(秒)" 
              prop="aram_auto_pick_delay"
              v-show="form.aram_auto_pick_enabled"
            >
              <div class="select-wrapper" :class="{ 'unsaved': isFieldChanged('aram_auto_pick_delay') }">
                <el-input-number 
                  v-model="form.aram_auto_pick_delay" 
                  :min="0"
                  :max="30"
                  :step="0.1"
                  :precision="1"
                  class="delay-input"
                />
              </div>
            </el-form-item>
          </div>

          <el-form-item 
            label="极地大乱斗自动选择英雄" 
            prop="aram_auto_pick_champions"
            v-show="form.aram_auto_pick_enabled"
          >
            <div class="select-wrapper" :class="{ 'unsaved': isFieldChanged('aram_auto_pick_champions') }">
              <el-select 
                v-model="form.aram_auto_pick_champions" 
                placeholder="请选择英雄" 
                filterable 
                clearable
                class="full-width"
                multiple
              >
                <el-option
                  v-for="hero in heroes"
                  :key="hero.id"
                  :label="hero.name"
                  :value="hero.id"
                >
                  <div class="hero-option">
                    <img 
                      :src="getResourceUrl('champion_icons', hero.id)" 
                      :alt="hero.name" 
                      class="hero-icon"
                    >
                    <span>{{ hero.name }}</span>
                  </div>
                </el-option>
              </el-select>
            </div>
          </el-form-item>

          <el-form-item label="自动选择英雄" prop="auto_pick_champions">
            <div class="select-wrapper" :class="{ 'unsaved': isFieldChanged('auto_pick_champions') }">
              <el-select 
                v-model="form.auto_pick_champions" 
                placeholder="请选择英雄" 
                filterable 
                clearable
                class="full-width"
                multiple
              >
                <el-option
                  v-for="hero in heroes"
                  :key="hero.id"
                  :label="hero.name"
                  :value="hero.id"
                >
                  <div class="hero-option">
                    <img 
                      :src="getResourceUrl('champion_icons', hero.id)" 
                      :alt="hero.name" 
                      class="hero-icon"
                    >
                    <span>{{ hero.name }}</span>
                  </div>
                </el-option>
              </el-select>
            </div>
          </el-form-item>

          <el-form-item label="自动禁用英雄" prop="auto_ban_champions">
            <div class="select-wrapper" :class="{ 'unsaved': isFieldChanged('auto_ban_champions') }">
              <el-select 
                v-model="form.auto_ban_champions" 
                placeholder="请选择禁用的英雄" 
                filterable 
                clearable
                class="full-width"
                multiple
              >
                <el-option
                  v-for="hero in heroes"
                  :key="hero.id"
                  :label="hero.name"
                  :value="hero.id"
                >
                  <div class="hero-option">
                    <img 
                      :src="getResourceUrl('champion_icons', hero.id)" 
                      :alt="hero.name" 
                      class="hero-icon"
                    >
                    <span>{{ hero.name }}</span>
                  </div>
                </el-option>
              </el-select>
            </div>
          </el-form-item>
        </el-col>
      </el-row>

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
          >导出设置</el-button>
        </div>
        
        <div class="right-buttons">
          <el-button 
            type="primary"
            @click="onSelectChampion()"
            class="select-champion-button"
          >选择英雄</el-button>
        </div>
      </div>
    </el-form>
  </div>
</template>

<script lang="ts" setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import type { FormInstance } from 'element-plus'
import { saveAs } from 'file-saver'

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
    
    // 加载英雄图标
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
      message: '保存失败，请稍后重试。',
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

// 添加选择英雄的方法
const onSelectChampion = async (): Promise<void> => {
  try {
    const response = await axios.post('/api/user_settings/select_champion')
    ElMessage({
      message: '英雄已选择！',
      type: 'success'
    })
    console.log('Response from server:', response.data)
  } catch (error) {
    ElMessage({
      message: '选择英雄失败，请稍后重试。',
      type: 'error'
    })
    console.error('Error selecting champion:', error)
  }
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

onMounted(() => {
  fetchDefaultSettings()
  fetchHeroes()
})
</script>

<style scoped>
.pre-game-setup {
  max-width: 800px;  /* 缩短最大宽度 */
  margin: 0 auto;
  padding: 20px;
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
  flex-direction: column;
  gap: 20px;
}

.custom-switch {
  margin-left: 8px;
}

.full-width {
  width: 100%;
}

.form-actions {
  margin-top: 24px;
  display: flex;
  justify-content: space-between;  /* 修改为space-between */
  align-items: center;
}

.left-buttons {
  display: flex;
  gap: 16px;
}

.right-buttons {
  margin-left: auto;  /* 确保右侧按钮靠右 */
}

.save-button,
.reset-button {
  min-width: 90px;
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

/* 按钮样式优化 */
.save-button {
  min-width: 90px;  /* 设置最小宽度确保按钮大小稳定 */
  transition: all 0.3s ease;
}

.reset-button {
  min-width: 70px;  /* 设置最小宽度 */
  margin-left: 12px;  /* 固定按钮间距 */
  transition: all 0.3s ease;
}

/* 文字切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .pre-game-setup {
    padding: 10px;
  }
  
  .switch-group :deep(.el-form-item) {
    margin-bottom: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .switch-group :deep(.el-form-item__content) {
    margin-left: 0 !important;
    flex: none !important;  /* 防止内容区域伸展 */
  }

  .switch-group :deep(.el-form-item__label) {
    line-height: 32px;
    margin-right: 12px;
    flex: 1;  /* 标签占据剩余空间 */
  }

  .custom-switch {
    margin-left: 0;  /* 移除左边距，因为现在使用flex布局 */
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
    margin-right: 8px;  /* 为未保存标识留出空间 */
  }

  .select-wrapper.unsaved {
    margin-right: 8px;  /* 为未保存标识留出空间 */
  }

  .select-wrapper.unsaved::after {
    right: -12px;
  }
}

.select-wrapper {
  position: relative;
  transition: all 0.3s ease;
  width: 100%;  /* 确保wrapper占满容器宽度 */
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

.full-width {
  width: 100%;  /* 确保select组件占满wrapper宽度 */
}

/* 响应式调整 */
@media (max-width: 768px) {

  .select-wrapper.unsaved {
    width: calc(100% - 20px);  /* 为未保存标识预留空间 */
    margin-right: 20px;  /* 增加右侧间距 */
  }
}

.hero-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.hero-icon {
  width: 24px;
  height: 24px;
  border-radius: 4px;
}

/* 调整下拉选项的高度和内边距 */
:deep(.el-select-dropdown__item) {
  height: 36px;
  line-height: 36px;
  padding: 0 12px;
}

/* 添加样式 */
.aram-settings {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  justify-content: space-between;
}

.delay-input {
  width: 230px;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .aram-settings {
    flex-direction: column;
    gap: 12px;
    justify-content: flex-start;
  }
  
  .delay-input {
    width: 100%;
  }
}
</style>