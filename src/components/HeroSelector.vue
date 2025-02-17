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
      <template #prefix>
        <div class="hero-icons-preview">
          <template v-for="hero in previewHeroes" :key="hero.id">
            <img 
              :src="getResourceUrl('champion_icons', hero.id)" 
              :alt="hero.name"
              class="preview-hero-icon"
              :title="hero.name"
            />
          </template>
          <span 
            v-if="remainingCount > 0" 
            class="remaining-count"
            :title="`还有${remainingCount}个英雄`"
          >
            +{{ remainingCount }}
          </span>
        </div>
      </template>
      
      <template #tag="{ option }">
        <span class="selected-tag">
          {{ getHeroName(option) }}
        </span>
      </template>

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
  title: string
  alias: string
  squarePortraitPath: string
}

type ResourceType = 'champion_icons'

const props = defineProps<{
  modelValue: number[]
  heroes: Hero[]
  getResourceUrl: (type: ResourceType, id: string | number) => string
  previewCount?: number
  enableEnglishSearch?: boolean
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

const previewHeroes = computed(() => {
  const count = props.previewCount ?? 3
  return selectedHeroes.value
    .slice(0, count)
    .map(id => props.heroes.find(hero => hero.id === id))
    .filter((hero): hero is Hero => hero !== undefined)
})

const getHeroName = (heroId: number) => {
  const hero = props.heroes.find(h => h.id === heroId)
  return hero?.name || ''
}

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
      const title = hero.title.toLowerCase()
      
      // 获取中文名的拼音和首字母
      const { 
        pinyin: titlePinyin, 
        firstLetters: titleFirstLetters, 
        firstLettersWithSpace: titleFirstLettersWithSpace 
      } = getPinyinAndFirstLetters(hero.title)
      
      // 基础搜索条件
      let matchConditions = [
        title.includes(lowercaseQuery),
        titlePinyin.includes(lowercaseQuery),
        titleFirstLetters.includes(queryNoSpace),
        titleFirstLettersWithSpace.includes(lowercaseQuery)
      ]
      
      // 如果启用英文名检索，添加英文名相关的搜索条件
      if (props.enableEnglishSearch) {
        const name = hero.name.toLowerCase()
        const { 
          pinyin: namePinyin, 
          firstLetters: nameFirstLetters, 
          firstLettersWithSpace: nameFirstLettersWithSpace 
        } = getPinyinAndFirstLetters(hero.name)
        
        matchConditions = matchConditions.concat([
          name.includes(lowercaseQuery),
          namePinyin.includes(lowercaseQuery),
          nameFirstLetters.includes(queryNoSpace),
          nameFirstLettersWithSpace.includes(lowercaseQuery)
        ])
      }
      
      return matchConditions.some(condition => condition)
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

const remainingCount = computed(() => {
  const count = props.previewCount ?? 3
  const total = selectedHeroes.value.length
  return total > count ? total - count : 0
})
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
  min-width: 120px;
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

.drag-item:hover {
  background-color: var(--el-fill-color-light);
}

.drag-item:hover .drag-handle {
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

/* 添加第一个英雄图标的样式 */
.first-hero-icon {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  margin-right: 6px;
  vertical-align: middle;
}

/* 自定义标签样式 */
.selected-tag {
  font-size: 12px;
  line-height: 1.2;
  vertical-align: middle;
}

/* 修改预览图标容器样式 */
.hero-icons-preview {
  display: flex;
  align-items: center;
  gap: 2px;
  padding-right: 6px;
  height: 24px; /* 确保容器高度固定 */
}

/* 修改预览英雄图标样式 */
.preview-hero-icon {
  width: 24px;
  height: 24px;
  border-radius: 4px;
  vertical-align: middle;
}

/* 调整选择框内部布局 */
:deep(.el-select__tags) {
  margin-left: 82px;  /* 调整为适应三个图标的宽度 */
}

:deep(.el-input__prefix) {
  display: flex;
  align-items: center;
  left: 8px;
}

:deep(.el-input__prefix-inner) {
  display: flex;
  align-items: center;
}

/* 调整选择框的内边距 */
:deep(.el-input__inner) {
  padding-left: 90px !important;  /* 调整为适应三个图标的宽度 */
}

/* 响应式调整 */
@media (max-width: 768px) {
  .preview-hero-icon {
    width: 20px;
    height: 20px;
  }
  
  :deep(.el-select__tags) {
    margin-left: 70px;
  }
  
  :deep(.el-input__inner) {
    padding-left: 76px !important;
  }
}

/* 添加剩余数量样式 */
.remaining-count {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  background-color: var(--el-fill-color-dark);
  color: var(--el-text-color-regular);
  font-size: 12px;
  border-radius: 4px;
  padding: 0 4px;
  font-weight: 500;
  cursor: default;
  transition: background-color 0.2s ease;
}

.remaining-count:hover {
  background-color: var(--el-fill-color-darker);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .remaining-count {
    min-width: 20px;
    height: 20px;
    font-size: 11px;
  }
}
</style> 