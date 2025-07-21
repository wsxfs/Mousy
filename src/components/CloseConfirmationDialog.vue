<template>
  <el-dialog
    v-model="dialogVisible"
    title="关闭确认"
    width="400px"
    :show-close="false"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    center
  >
    <div class="close-dialog-content">
      <p>您想要最小化到托盘还是完全关闭应用程序？</p>
      <el-checkbox v-model="rememberChoice" label="记住我的选择" />
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="handleCancel">取消</el-button>
        <el-button @click="handleMinimize" type="primary">最小化到托盘</el-button>
        <el-button @click="handleClose" type="danger">完全关闭</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue';

// 对话框可见性
const dialogVisible = ref(false);

// 记住选择复选框
const rememberChoice = ref(false);

// 处理最小化到托盘
const handleMinimize = () => {
  window.ipcRenderer.send('close-dialog-response', {
    action: 'minimize',
    rememberChoice: rememberChoice.value
  });
  dialogVisible.value = false;
};

// 处理完全关闭
const handleClose = () => {
  window.ipcRenderer.send('close-dialog-response', {
    action: 'close',
    rememberChoice: rememberChoice.value
  });
  dialogVisible.value = false;
};

// 处理取消
const handleCancel = () => {
  window.ipcRenderer.send('close-dialog-response', {
    action: 'cancel',
    rememberChoice: false
  });
  dialogVisible.value = false;
};

// 显示对话框的处理函数
const showDialog = () => {
  dialogVisible.value = true;
  rememberChoice.value = false;
};

// 监听来自主进程的显示对话框请求
onMounted(() => {
  window.ipcRenderer.on('show-close-dialog', showDialog);
});

// 清理监听器
onUnmounted(() => {
  window.ipcRenderer.off('show-close-dialog', showDialog);
});
</script>

<style scoped>
.close-dialog-content {
  margin-bottom: 20px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}
</style>