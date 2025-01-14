<template>
  <div 
    class="hero-search-container"
    @dragover.prevent
    @drop.prevent
  >
    <el-select 
      v-model="selectedHeroes" 
      placeholder="已选择的英雄" 
      class="selected-heroes"
      multiple
      :collapse-tags="true"
      :collapse-tags-tooltip="true"
    >
      <div class="sortable-container" ref="sortableRef">
        <el-option
          v-for="hero in selectedHerosList"
          :key="hero.id"
          :label="hero.name"
          :value="hero.id"
        >
          <div class="hero-option sortable-item">
            <div class="drag-area">
              <div class="drag-handle">
                <div class="drag-lines">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
            <img 
              :src="getResourceUrl('champion_icons', hero.id)" 
              :alt="hero.name" 
              class="hero-icon"
            >
            <span class="hero-name">{{ hero.name }}</span>
          </div>
        </el-option>
      </div>
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
import { ref, computed, onMounted, nextTick } from 'vue'
import { Check } from '@element-plus/icons-vue'
import { pinyin } from 'pinyin-pro'
import Sortable from 'sortablejs'

interface Hero {
  id: number
  name: string
  alias: string
  squarePortraitPath: string
}

type ResourceType = 'champion_icons'

const props = defineProps<{
  modelValue: number[]
  heroes: Hero[]
  getResourceUrl: (type: ResourceType, id: string | number) => string
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: number[]): void
}>()

const selectedHeroes = computed({
  get: () => props.modelValue,
  set: (value: number[]) => emit('update:modelValue', value)
})

const selectedHerosList = computed(() => {
  return props.modelValue
    .map(id => props.heroes.find(hero => hero.id === id))
    .filter((hero): hero is Hero => hero !== undefined)
})

const tempSelectedHero = ref<number | ''>('')
const searchLoading = ref(false)
const filteredHeroes = ref<Hero[]>([])

const sortableRef = ref<HTMLElement | null>(null)

onMounted(() => {
  nextTick(() => {
    if (sortableRef.value) {
      Sortable.create(sortableRef.value, {
        animation: 150,
        handle: '.drag-handle',
        onEnd: ({ oldIndex, newIndex }) => {
          if (oldIndex !== undefined && newIndex !== undefined) {
            const newOrder = [...selectedHeroes.value]
            const [movedItem] = newOrder.splice(oldIndex, 1)
            newOrder.splice(newIndex, 0, movedItem)
            selectedHeroes.value = newOrder
          }
        },
        ghostClass: 'sortable-ghost',
        chosenClass: 'sortable-chosen',
        dragClass: 'sortable-drag',
        forceFallback: true
      })
    }
  })
})

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

const handleHeroSelect = (heroId: number) => {
  if (!selectedHeroes.value.includes(heroId)) {
    selectedHeroes.value = [...selectedHeroes.value, heroId]
  }
  tempSelectedHero.value = ''
}

const handleHeroClick = (heroId: number) => {
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
  gap: 6px;
  padding: 2px 0px 2px 0px;
  position: relative;
  cursor: pointer;
  width: 100%;
  font-weight: normal;
  border-radius: 4px;
  transition: background-color 0.2s ease;
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
  width: 20px;
  height: 20px;
  border-radius: 3px;
}

.hero-name {
  font-size: 13px;
}

.drag-area {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 100%;
  cursor: move;
  padding: 0 0px;
}

.drag-handle {
  opacity: 0.3;
  transition: all 0.15s ease;
}

.drag-lines {
  display: flex;
  flex-direction: column;
  gap: 3px;
  padding: 2px;
}

.drag-lines span {
  width: 12px;
  height: 1.5px;
  background-color: currentColor;
  border-radius: 1px;
  display: block;
}

.sortable-item:hover {
  background-color: var(--el-fill-color-light);
}

.sortable-item:hover .drag-handle {
  opacity: 0.6;
}

.sortable-ghost {
  background-color: var(--el-color-primary-light-9);
  border: 1px dashed var(--el-color-primary);
  opacity: 0.8;
}

.sortable-chosen {
  background-color: var(--el-color-primary-light-9);
}

.sortable-drag {
  opacity: 0.9;
}

:deep(.el-select-dropdown__item) {
  padding: 0;
  height: auto;
}

:deep(.el-select-dropdown__item.selected) {
  font-weight: normal;
}

:deep(.el-select-dropdown__item.hover) {
  background-color: transparent;
}

/* 添加分隔线 */
:deep(.el-select-dropdown__item:not(:last-child)) {
  border-bottom: 1px solid var(--el-border-color-lighter);
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
</style> 