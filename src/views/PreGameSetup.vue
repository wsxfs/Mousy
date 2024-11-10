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
          <el-form-item label="自动选择英雄" prop="auto_pick_champions">
            <div class="select-wrapper" :class="{ 'unsaved': isFieldChanged('auto_pick_champions') }">
              <el-select 
                v-model="form.auto_pick_champions" 
                placeholder="请选择英雄" 
                filterable 
                clearable
                class="full-width"
              >
                <el-option
                  v-for="hero in heroes"
                  :key="hero.id"
                  :label="hero.name"
                  :value="hero.name"
                ></el-option>
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
              >
                <el-option
                  v-for="hero in heroes"
                  :key="hero.id"
                  :label="hero.name"
                  :value="hero.name"
                ></el-option>
              </el-select>
            </div>
          </el-form-item>
        </el-col>
      </el-row>

      <div class="form-actions">
        <el-button 
          :type="hasUnsavedChanges ? 'warning' : 'primary'"
          @click="onSubmit()"
          class="save-button"
        >
          <transition name="fade" mode="out-in">
            <span :key="hasUnsavedChanges">
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
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, computed } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 表单引用
const formRef = ref(null)

// 存储默认值
const defaultSettings = ref(null)

// 表单数据
const form = reactive({
  auto_accept: false,
  auto_pick_champions: '',
  auto_ban_champions: '',
  auto_accept_swap_position: false,
  auto_accept_swap_champion: false,
})

// 记录最后一次成功保存的状态
const lastSavedState = ref(null)

// 计算是否有未保存的更改
const hasUnsavedChanges = computed(() => {
  if (!lastSavedState.value) return false
  return Object.keys(form).some(key => form[key] !== lastSavedState.value[key])
})

// 获取默认设置
const fetchDefaultSettings = async () => {
  try {
    const response = await axios.get('/api/user_settings/get')
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

// 组件挂载时获取默认设置
onMounted(() => {
  fetchDefaultSettings()
})

// 英雄列表
const heroes = [
  { id: 1, name: '英雄A' },
  { id: 2, name: '英雄B' },
  { id: 3, name: '英雄C' },
  // 可据需要添加更多英雄
]

// 提交表单
const onSubmit = async () => {
  try {
    const response = await axios.post('/api/user_settings/update_all', form)
    // 保存成功后，更新最后保存的状态
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
const onReset = () => {
  if (lastSavedState.value) {
    Object.assign(form, lastSavedState.value)
  }
}

// 检查特定字段是否有更改
const isFieldChanged = (fieldName) => {
  if (!lastSavedState.value) return false
  return form[fieldName] !== lastSavedState.value[fieldName]
}
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
  justify-content: flex-start;
  gap: 16px;
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
  
  .save-button,
  .reset-button {
    width: 100%;
    margin: 5px 0;
  }

  .reset-button {
    margin-left: 0;  /* 移动端下移除左边距 */
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
</style>