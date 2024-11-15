<template>
  <div class="champion-detail">
    <h2>英雄详情页 - {{ championId }}</h2>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  championId: number
}>()
</script>