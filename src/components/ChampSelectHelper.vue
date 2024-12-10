<template>
  <el-dialog
    :model-value="visible"
    @update:model-value="emit('update:visible', $event)"
    title="选人助手"
    :close-on-click-modal="false"
    width="400px"
    destroy-on-close
  >
    <div class="champ-select-helper">
      <div class="game-mode-info">
        <h3>当前游戏模式</h3>
        <p>{{ gameMode || '未知' }}</p>
      </div>
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed, watch } from 'vue'
import { useGameStateStore } from '../stores/gameState'

const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
}>()

const gameStateStore = useGameStateStore()

// 监听对话框可见性变化
watch(() => props.visible, async (newVisible) => {
  if (newVisible) {
    await gameStateStore.fetchGameMode()
  }
})

const gameMode = computed(() => gameStateStore.gameMode)
</script>

<style scoped>
.champ-select-helper {
  padding: 20px;
}

.game-mode-info {
  text-align: center;
}

.game-mode-info h3 {
  margin-bottom: 10px;
  color: var(--el-text-color-primary);
}

.game-mode-info p {
  font-size: 18px;
  color: var(--el-color-primary);
}
</style>