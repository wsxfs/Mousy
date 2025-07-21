<template>
  <div class="user-settings">
    <div class="settings-header">
      <h2 class="settings-title">用户设置</h2>
    </div>

    <el-card class="settings-card">
      <template #header>
        <div class="card-header">
          <span>用户偏好</span>
        </div>
      </template>

      <div class="settings-section">
        <div class="setting-item">
          <div class="setting-label">点击关闭时</div>
          <div class="setting-control">
            <el-select v-model="closePreference">
              <el-option label="每次询问" value="ask" />
              <el-option label="最小化到托盘" value="minimize" />
              <el-option label="完全关闭" value="close" />
            </el-select>
          </div>
        </div>
      </div>
      
      <div class="settings-actions">
        <el-button type="primary" @click="saveClosePreference">保存设置</el-button>
        <el-button @click="fetchClosePreference">重置</el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import axios from 'axios';

// 关闭偏好设置
const closePreference = ref('ask');

// 获取当前关闭偏好设置
const fetchClosePreference = async () => {
  try {
    // 先尝试获取专门的关闭偏好设置API
    try {
      const response = await axios.get('/api/user_settings/get_close_preference');
      const settings = response.data;
      
      if (settings && settings.rememberChoice) {
        closePreference.value = settings.action;
      } else {
        closePreference.value = 'ask';
      }
      return;
    } catch (e) {
      console.warn('专用API不可用，尝试通用设置API');
    }
    
    // 如果专用API失败，尝试从通用设置API获取
    const response = await axios.get('/api/user_settings/get');
    const settings = response.data;
    
    if (settings.closePreference && settings.closePreference.rememberChoice) {
      closePreference.value = settings.closePreference.action;
    } else {
      closePreference.value = 'ask';
    }
  } catch (error) {
    console.error('获取关闭偏好设置失败:', error);
    ElMessage.error('获取设置失败');
  }
};

// 保存关闭偏好设置
const saveClosePreference = async () => {
  try {
    if (closePreference.value === 'ask') {
      // 重置关闭偏好设置
      await axios.post('/api/user_settings/reset_close_preference');
      ElMessage.success('设置已保存');
    } else {
      try {
        // 先尝试使用专用API
        const settings = {
          closePreference: {
            action: closePreference.value,
            rememberChoice: true,
            timestamp: Date.now()
          }
        };
        await axios.post('/api/user_settings/update_close_preference', settings);
        ElMessage.success('设置已保存');
        return;
      } catch (e) {
        console.warn('专用API不可用，尝试通用设置API');
      }
      
      // 如果专用API失败，尝试使用通用设置API
      // 先获取当前所有设置
      const response = await axios.get('/api/user_settings/get');
      const allSettings = response.data;
      
      // 更新关闭偏好设置
      allSettings.closePreference = {
        action: closePreference.value,
        rememberChoice: true,
        timestamp: Date.now()
      };
      
      // 保存所有设置
      await axios.post('/api/user_settings/update_all', allSettings);
      ElMessage.success('设置已保存');
    }
  } catch (error) {
    console.error('保存关闭偏好设置失败:', error);
    ElMessage.error('保存设置失败');
  }
};

// 页面加载时获取当前设置
onMounted(() => {
  fetchClosePreference();
});
</script>

<style scoped>
.user-settings {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px;
}

.settings-header {
  margin-bottom: 20px;
}

.settings-title {
  font-size: 1.5rem;
  color: var(--el-text-color-primary);
  margin: 0;
  padding-left: 12px;
  position: relative;
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
}

.card-header {
  font-size: 16px;
  font-weight: 500;
}

.settings-section {
  padding: 10px 0;
}

.setting-item {
  display: flex;
  align-items: center;
  padding: 10px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-label {
  flex: 1;
  font-size: 14px;
  color: var(--el-text-color-primary);
}

.setting-control {
  width: 200px;
}
</style>