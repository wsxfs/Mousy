<template>
  <div class="notebook-container">
    <el-tabs v-model="activeTab" type="card">
      <el-tab-pane label="黑名单" name="blacklist">
        <div class="list-header">
          <el-button type="primary" @click="handleAdd('black')">
            <el-icon><Plus /></el-icon>添加记录
          </el-button>
          <el-input
            v-model="searchQuery"
            placeholder="搜索召唤师"
            clearable
            class="search-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <el-table :data="filteredBlacklist" style="width: 100%">
          <el-table-column prop="summonerName" label="召唤师名称" />
          <el-table-column prop="summonerId" label="召唤师ID" width="120" />
          <el-table-column prop="region" label="大区" width="100" />
          <el-table-column prop="reason" label="罪行" width="150" />
          <el-table-column prop="details" label="详情" show-overflow-tooltip />
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button-group>
                <el-button type="primary" size="small" @click="handleEdit(scope.row)">
                  编辑
                </el-button>
                <el-button type="danger" size="small" @click="handleDelete(scope.row)">
                  删除
                </el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="白名单" name="whitelist">
        <div class="list-header">
          <el-button type="primary" @click="handleAdd('white')">
            <el-icon><Plus /></el-icon>添加记录
          </el-button>
          <el-input
            v-model="searchQuery"
            placeholder="搜索召唤师"
            clearable
            class="search-input"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
        </div>

        <el-table :data="filteredWhitelist" style="width: 100%">
          <el-table-column prop="summonerName" label="召唤师名称" />
          <el-table-column prop="summonerId" label="召唤师ID" width="120" />
          <el-table-column prop="region" label="大区" width="100" />
          <el-table-column prop="reason" label="亮点" width="150" />
          <el-table-column prop="details" label="详情" show-overflow-tooltip />
          <el-table-column label="操作" width="150">
            <template #default="scope">
              <el-button-group>
                <el-button type="primary" size="small" @click="handleEdit(scope.row)">
                  编辑
                </el-button>
                <el-button type="danger" size="small" @click="handleDelete(scope.row)">
                  删除
                </el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogType === 'add' ? '添加记录' : '编辑记录'"
      width="500px"
    >
      <el-form :model="formData" label-width="100px">
        <el-form-item label="召唤师名称">
          <el-input v-model="formData.summonerName" />
        </el-form-item>
        <el-form-item label="召唤师ID">
          <el-input v-model="formData.summonerId" />
        </el-form-item>
        <el-form-item label="大区">
          <el-select v-model="formData.region" placeholder="选择大区">
            <el-option label="艾欧尼亚" value="艾欧尼亚" />
            <el-option label="祖安" value="祖安" />
            <el-option label="诺克萨斯" value="诺克萨斯" />
            <!-- 添加更多大区选项 -->
          </el-select>
        </el-form-item>
        <el-form-item :label="currentListType === 'black' ? '罪行' : '亮点'">
          <el-input v-model="formData.reason" />
        </el-form-item>
        <el-form-item label="详情">
          <el-input
            v-model="formData.details"
            type="textarea"
            :rows="4"
            placeholder="请输入详细信息"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogVisible = false">取消</el-button>
          <el-button type="primary" @click="handleSubmit">确定</el-button>
        </span>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { Plus, Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'

interface SummonerRecord {
  id: number
  summonerName: string
  summonerId: string
  region: string
  reason: string
  details: string
}

const activeTab = ref('blacklist')
const searchQuery = ref('')
const dialogVisible = ref(false)
const dialogType = ref<'add' | 'edit'>('add')
const currentListType = ref<'black' | 'white'>('black')

// 模拟数据
const blacklist = ref<SummonerRecord[]>([])
const whitelist = ref<SummonerRecord[]>([])

const formData = ref<SummonerRecord>({
  id: 0,
  summonerName: '',
  summonerId: '',
  region: '',
  reason: '',
  details: ''
})

// 过滤后的列表
const filteredBlacklist = computed(() => {
  return blacklist.value.filter(item =>
    item.summonerName.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    item.summonerId.includes(searchQuery.value)
  )
})

const filteredWhitelist = computed(() => {
  return whitelist.value.filter(item =>
    item.summonerName.toLowerCase().includes(searchQuery.value.toLowerCase()) ||
    item.summonerId.includes(searchQuery.value)
  )
})

// 处理添加记录
const handleAdd = (type: 'black' | 'white') => {
  dialogType.value = 'add'
  currentListType.value = type
  formData.value = {
    id: Date.now(),
    summonerName: '',
    summonerId: '',
    region: '',
    reason: '',
    details: ''
  }
  dialogVisible.value = true
}

// 处理编辑记录
const handleEdit = (row: SummonerRecord) => {
  dialogType.value = 'edit'
  formData.value = { ...row }
  dialogVisible.value = true
}

// 处理删除记录
const handleDelete = (row: SummonerRecord) => {
  ElMessageBox.confirm(
    '确定要删除这条记录吗？',
    '警告',
    {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    const list = activeTab.value === 'blacklist' ? blacklist : whitelist
    const index = list.value.findIndex(item => item.id === row.id)
    if (index !== -1) {
      list.value.splice(index, 1)
      ElMessage.success('删除成功')
    }
  }).catch(() => {})
}

// 处理提交
const handleSubmit = () => {
  const list = currentListType.value === 'black' ? blacklist : whitelist
  if (dialogType.value === 'add') {
    list.value.push({ ...formData.value })
  } else {
    const index = list.value.findIndex(item => item.id === formData.value.id)
    if (index !== -1) {
      list.value[index] = { ...formData.value }
    }
  }
  dialogVisible.value = false
  ElMessage.success(dialogType.value === 'add' ? '添加成功' : '更新成功')
}
</script>

<style scoped>
.notebook-container {
  padding: 20px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.search-input {
  width: 300px;
}

.el-table {
  margin-top: 20px;
}

:deep(.el-table__row) {
  cursor: pointer;
}

:deep(.el-table__row:hover) {
  background-color: var(--el-table-row-hover-bg-color);
}
</style> 