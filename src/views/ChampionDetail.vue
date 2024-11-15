<template>
  <div class="champion-detail">
    <h2>英雄详情页 - {{ championId }}</h2>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const championId = ref(route.params.championId)
</script>