<template>
  <div 
    class="user-settings"
    @dragover.prevent="handleDragOver"
    @dragleave.prevent="handleDragLeave"
    @drop.prevent="handleDrop"
    :data-dragging="isDragging"
  >
    <div class="settings-header">
      <div class="header-content">
        <h2 class="settings-title">用户设置</h2>
      </div>
    </div>

    <el-form :model="form" label-position="top" ref="formRef" class="settings-form">
      <el-card class="settings-card">
        <template #header>
          <div class="card-header">
            <span>用户偏好</span>
          </div>
        </template>

        <div class="settings-section">
          <div class="setting-item">
            <div class="setting-label">点击关闭时</div>
            <div class="setting-control" :class="{ 'unsaved': isFieldChanged('closePreference') }">
              <el-select v-model="form.closePreference.action">
                <el-option label="每次询问" value="ask" />
                <el-option label="记住：最小化到托盘" value="minimize" />
                <el-option label="记住：完全关闭" value="close" />
              </el-select>
            </div>
          </div>
        </div>
      </el-card>

      <!-- 底部操作按钮 -->
      <el-card class="settings-card action-card">
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
          </div>
        </div>
      </el-card>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { ElMessage } from 'element-plus';
import axios from 'axios';
import type { FormInstance } from 'element-plus';

// 表单引用
const formRef = ref<FormInstance>();

// 创建一个指向8001端口的axios实例
const electronApi = axios.create({
  baseURL: 'http://127.0.0.1:8001'
});

// 表单数据
const form = reactive({
  closePreference: {
    action: 'ask',
    rememberChoice: false, // 默认不记住选择
    timestamp: Date.now()
  }
});

// 记录最后一次成功保存的状态
const lastSavedState = ref<any>(null);

// 拖拽状态
const isDragging = ref(false);

// 计算是否有未保存的更改
const hasUnsavedChanges = computed(() => {
  if (!lastSavedState.value) return false;

  // 递归比较对象
  const isObjectChanged = (current: any, saved: any): boolean => {
    if (current === saved) return false;
    
    if (typeof current !== 'object' || current === null ||
        typeof saved !== 'object' || saved === null) {
      return current !== saved;
    }
    
    const currentKeys = Object.keys(current);
    const savedKeys = Object.keys(saved);
    
    if (currentKeys.length !== savedKeys.length) return true;
    
    return currentKeys.some(key => isObjectChanged(current[key], saved[key]));
  };

  return isObjectChanged(form, lastSavedState.value);
});

// 添加深拷贝函数
const deepClone = <T>(obj: T): T => {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }
  
  if (Array.isArray(obj)) {
    return obj.map(item => deepClone(item)) as unknown as T;
  }
  
  const cloned = {} as T;
  Object.keys(obj as object).forEach(key => {
    cloned[key as keyof T] = deepClone((obj as any)[key]);
  });
  return cloned;
};

// 获取当前关闭偏好设置
const fetchSettings = async (): Promise<void> => {
  try {
    console.log('获取当前关闭偏好设置');
    
    // 先尝试从Electron配置管理器获取
    try {
      // 添加时间戳防止缓存
      const timestamp = Date.now();
      const response = await electronApi.get(`/api/user_settings/get_close_preference?_=${timestamp}`);
      const settings = response.data;
      
      console.log('从API获取的关闭偏好设置:', settings);
      
      if (settings && settings.action) {
        // 如果有设置，使用服务器返回的设置
        form.closePreference = deepClone(settings);
        
        // 确保"每次询问"选项对应 rememberChoice: false
        if (form.closePreference.action === 'ask') {
          form.closePreference.rememberChoice = false;
        }
        
        console.log('设置表单数据为:', form.closePreference);
      } else {
        // 如果没有设置，默认为"每次询问"
        form.closePreference = {
          action: 'ask',
          rememberChoice: false,
          timestamp: Date.now()
        };
        console.log('没有设置，使用默认值:', form.closePreference);
      }
      
      // 记录初始状态为已保存状态
      lastSavedState.value = deepClone(form);
      return;
    } catch (e) {
      console.warn('Electron API不可用，尝试FastAPI:', e);
    }
    
    // 如果Electron API失败，尝试从FastAPI获取
    // 添加时间戳防止缓存
    const timestamp = Date.now();
    const response = await axios.get(`/api/user_settings/get?_=${timestamp}`);
    const settings = response.data;
    
    console.log('从FastAPI获取的所有设置:', settings);
    
    if (settings.closePreference && settings.closePreference.action) {
      form.closePreference = deepClone(settings.closePreference);
      
      // 确保"每次询问"选项对应 rememberChoice: false
      if (form.closePreference.action === 'ask') {
        form.closePreference.rememberChoice = false;
      }
      
      console.log('设置表单数据为:', form.closePreference);
    } else {
      form.closePreference = {
        action: 'ask',
        rememberChoice: false,
        timestamp: Date.now()
      };
      console.log('没有设置，使用默认值:', form.closePreference);
    }
    
    // 记录初始状态为已保存状态
    lastSavedState.value = deepClone(form);
  } catch (error) {
    console.error('获取设置失败:', error);
    ElMessage.error('获取设置失败');
  }
};

// 提交表单
const onSubmit = async (): Promise<void> => {
  try {
    // 根据选择的操作更新表单数据
    if (form.closePreference.action === 'ask') {
      // "每次询问"选项应该完全清除关闭偏好设置
      console.log('选择了"每次询问"，清除关闭偏好设置');
      
      try {
        // 重置关闭偏好设置
        await electronApi.post('/api/user_settings/reset_close_preference');
        
        // 更新本地表单状态
        form.closePreference = {
          action: 'ask',
          rememberChoice: false,
          timestamp: Date.now()
        };
      } catch (e) {
        console.warn('Electron API不可用，尝试FastAPI');
        await axios.post('/api/user_settings/reset_close_preference');
        
        // 更新本地表单状态
        form.closePreference = {
          action: 'ask',
          rememberChoice: false,
          timestamp: Date.now()
        };
      }
    } else {
      // "最小化到托盘"或"完全关闭"选项应该设置 rememberChoice 为 true
      console.log(`选择了"${form.closePreference.action}"，设置rememberChoice为true`);
      form.closePreference.rememberChoice = true;
      
      try {
        // 先尝试使用Electron API
        const settings = {
          closePreference: form.closePreference
        };
        console.log('保存设置到Electron API:', settings);
        await electronApi.post('/api/user_settings/update_close_preference', settings);
      } catch (e) {
        console.warn('Electron API不可用，尝试FastAPI');
        
        // 如果Electron API失败，尝试使用FastAPI
        // 先获取当前所有设置
        const response = await axios.get('/api/user_settings/get');
        const allSettings = response.data;
        
        // 更新关闭偏好设置
        allSettings.closePreference = form.closePreference;
        
        // 保存所有设置
        console.log('保存设置到FastAPI:', allSettings);
        await axios.post('/api/user_settings/update_all', allSettings);
      }
    }
    
    // 更新保存状态
    lastSavedState.value = deepClone(form);
    ElMessage({
      message: '设置已保存！',
      type: 'success'
    });
    
    // 等待一小段时间，确保设置已经保存到后端
    await new Promise(resolve => setTimeout(resolve, 500));
    
    // 重新获取设置，确保UI显示与实际保存的设置一致
    await fetchSettings();
  } catch (error) {
    ElMessage({
      message: '保存失败，请稍后再试。',
      type: 'error'
    });
    console.error('保存设置失败:', error);
  }
};

// 重置表单
const onReset = (): void => {
  if (lastSavedState.value) {
    Object.assign(form, deepClone(lastSavedState.value));
  }
};

// 检查特定字段是否有更改
const isFieldChanged = (path: string): boolean => {
  if (!lastSavedState.value) return false;
  
  // 处理嵌套路径
  const getNestedValue = (obj: any, path: string): any => {
    return path.split('.').reduce((prev, curr) => {
      return prev?.[curr];
    }, obj);
  };
  
  const currentValue = getNestedValue(form, path);
  const savedValue = getNestedValue(lastSavedState.value, path);
  
  // 处理数组类型
  if (Array.isArray(currentValue) && Array.isArray(savedValue)) {
    if (currentValue.length !== savedValue.length) return true;
    return JSON.stringify(currentValue) !== JSON.stringify(savedValue);
  }
  
  // 处理对象类型
  if (typeof currentValue === 'object' && currentValue !== null &&
      typeof savedValue === 'object' && savedValue !== null) {
    return JSON.stringify(currentValue) !== JSON.stringify(savedValue);
  }
  
  // 处理基本类型
  return currentValue !== savedValue;
};

// 处理拖拽悬停
const handleDragOver = (event: DragEvent) => {
  // 检查是否是文件拖拽
  if (!event.dataTransfer?.types.includes('Files')) return;
  
  event.preventDefault();
  isDragging.value = true;
};

// 处理拖拽离开
const handleDragLeave = (event: DragEvent) => {
  // 检查是否是文件拖拽
  if (!event.dataTransfer?.types.includes('Files')) return;
  
  event.preventDefault();
  isDragging.value = false;
};

// 处理拖拽放下
const handleDrop = async (event: DragEvent) => {
  // 检查是否是文件拖拽
  if (!event.dataTransfer?.types.includes('Files')) return;
  
  event.preventDefault();
  isDragging.value = false;
  
  try {
    const file = event.dataTransfer?.files[0];
    if (!file || !file.name.endsWith('.json')) {
      ElMessage({
        message: '请拖入有效的 JSON 设置文件',
        type: 'warning'
      });
      return;
    }

    const text = await file.text();
    const importedSettings = JSON.parse(text);
    
    if (importedSettings.closePreference) {
      form.closePreference = importedSettings.closePreference;
      ElMessage({
        message: '设置已导入！',
        type: 'success'
      });
    } else {
      ElMessage({
        message: '导入的文件不包含关闭偏好设置',
        type: 'warning'
      });
    }
  } catch (error) {
    ElMessage({
      message: '导入失败，请确保文件格式正确',
      type: 'error'
    });
  }
};

// 页面加载时获取当前设置
onMounted(() => {
  fetchSettings();
});
</script>

<style scoped>
.user-settings {
  max-width: 940px;
  margin: 0 auto;
  padding: 12px;
  position: relative;
  min-height: 200px;
  border: 2px dashed transparent;
  transition: all 0.3s ease;
}

.user-settings[data-dragging="true"] {
  border-color: var(--el-color-primary);
  background-color: rgba(var(--el-color-primary-rgb), 0.05);
}

.user-settings::after {
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

.user-settings[data-dragging="true"]::after {
  opacity: 0.7;
}

.settings-header {
  margin-bottom: 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
}

.settings-title {
  margin: 0;
  font-size: 1.4rem;
  color: #303133;
  white-space: nowrap;
  position: relative;
  padding-left: 12px;
}

.settings-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 50%;
  transform: translateY(-50%);
  width: 3px;
  height: 20px;
  background: var(--el-color-primary);
  border-radius: 2px;
}

.settings-card {
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.05);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 16px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.settings-section {
  padding: 10px 0;
}

.setting-item {
  display: flex;
  align-items: center;
  padding: 10px 0;
  margin-bottom: 10px;
}

.setting-label {
  flex: 1;
  font-size: 14px;
  color: var(--el-text-color-regular);
}

.setting-control {
  width: 200px;
  position: relative;
  transition: all 0.3s ease;
}

.setting-control.unsaved::after {
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

@keyframes pulse {
  0% {
    transform: translateY(-50%) scale(1);
    opacity: 1;
  }
  50% {
    transform: translateY(-50%) scale(1.2);
    opacity: 0.8;
  }
  100% {
    transform: translateY(-50%) scale(1);
    opacity: 1;
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

.primary-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.save-button,
.reset-button {
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

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(2px);
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
</style>