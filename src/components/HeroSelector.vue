<template>
  <div class="hero-search-container">
    <el-select 
      v-model="selectedHeroes" 
      placeholder="已选择的英雄" 
      class="selected-heroes"
      multiple
      :collapse-tags="true"
      :collapse-tags-tooltip="true"
    >
      <el-option
        v-for="hero in selectedHerosList"
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
    
    <el-select
      v-model="tempSelectedHero"
      filterable
      remote
      reserve-keyword
      placeholder="搜索英雄"
      :remote-method="handleHeroSearch"
      :loading="searchLoading"
      class="hero-search"
      @change="handleHeroSelect"
    >
      <el-option
        v-for="hero in filteredHeroes"
        :key="hero.id"
        :label="hero.name"
        :value="hero.id"
      >
        <div 
          class="hero-option" 
          :class="{ 'hero-selected': selectedHeroes.includes(hero.id) }"
          @click.stop="handleHeroClick(hero.id)"
        >
          <img 
            :src="getResourceUrl('champion_icons', hero.id)" 
            :alt="hero.name" 
            class="hero-icon"
          >
          <span>{{ hero.name }}</span>
          <el-icon v-if="selectedHeroes.includes(hero.id)" class="check-icon">
            <Check />
          </el-icon>
        </div>
      </el-option>
    </el-select>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Check } from '@element-plus/icons-vue'
import { pinyin } from 'pinyin-pro'

interface Hero {
  id: string
  name: string
  alias: string
  squarePortraitPath: string
}

const props = defineProps<{
  modelValue: string[]
  heroes: Hero[]
  getResourceUrl: (type: string, id: string) => string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string[]): void
}>()

const selectedHeroes = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const selectedHerosList = computed(() => {
  return props.modelValue
    .map(id => props.heroes.find(hero => hero.id === id))
    .filter((hero): hero is Hero => hero !== undefined)
})

const tempSelectedHero = ref('')
const searchLoading = ref(false)
const filteredHeroes = ref<Hero[]>([])

const getPinyinAndFirstLetters = (text: string) => {
  const pinyinText = pinyin(text, { toneType: 'none' })
  const firstLetters = pinyin(text, { pattern: 'first', toneType: 'none' }).replace(/\s/g, '')
  const firstLettersWithSpace = pinyin(text, { pattern: 'first', toneType: 'none' })
  return {
    pinyin: pinyinText.toLowerCase(),
    firstLetters: firstLetters.toLowerCase(),
    firstLettersWithSpace: firstLettersWithSpace.toLowerCase()
  }
}

const handleHeroSearch = (query: string) => {
  if (query) {
    const lowercaseQuery = query.toLowerCase()
    const queryNoSpace = lowercaseQuery.replace(/\s/g, '')
    
    filteredHeroes.value = props.heroes.filter(hero => {
      const name = hero.name.toLowerCase()
      const { pinyin: namePinyin, firstLetters, firstLettersWithSpace } = getPinyinAndFirstLetters(hero.name)
      
      return name.includes(lowercaseQuery) || 
             namePinyin.includes(lowercaseQuery) || 
             firstLetters.includes(queryNoSpace) ||
             firstLettersWithSpace.includes(lowercaseQuery)
    })
  } else {
    filteredHeroes.value = props.heroes
  }
}

const handleHeroSelect = (heroId: string) => {
  if (!selectedHeroes.value.includes(heroId)) {
    selectedHeroes.value = [...selectedHeroes.value, heroId]
  }
  tempSelectedHero.value = ''
}

const handleHeroClick = (heroId: string) => {
  if (selectedHeroes.value.includes(heroId)) {
    selectedHeroes.value = selectedHeroes.value.filter(id => id !== heroId)
  } else {
    selectedHeroes.value = [...selectedHeroes.value, heroId]
  }
  tempSelectedHero.value = ''
}
</script>

<style scoped>
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

/* 响应式调整 */
@media (max-width: 768px) {
  .hero-search-container {
    flex-direction: column;
  }
  
  .selected-heroes,
  .hero-search {
    width: 100%;
  }
}

/* 确保 el-select 中的选项也使用相同的字体样式 */
:deep(.el-select-dropdown__item.selected) {
  color: var(--el-color-primary);
  font-weight: normal;
}
</style> 