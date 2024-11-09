<template>
  <div class="pre-game-setup">
    <el-container>
      <el-header>
        <h2>赛前预设</h2>
      </el-header>
      <el-main>
        <el-form :model="form" label-width="130px" ref="formRef">
          <!-- 自动接受对局 -->
          <el-form-item label="自动接受对局" prop="auto_accept">
            <el-switch v-model="form.auto_accept"></el-switch>
          </el-form-item>

          <!-- 自动选择英雄 -->
          <el-form-item label="自动选择英雄" prop="auto_pick_champions">
            <el-select v-model="form.auto_pick_champions" placeholder="请选择英雄">
              <el-option
                v-for="hero in heroes"
                :key="hero.id"
                :label="hero.name"
                :value="hero.name"
              ></el-option>
            </el-select>
          </el-form-item>

          <!-- 自动禁用英雄 -->
          <el-form-item label="自动禁用英雄" prop="auto_ban_champions">
            <el-select v-model="form.auto_ban_champions" placeholder="请选择禁用的英雄">
              <el-option
                v-for="hero in heroes"
                :key="hero.id"
                :label="hero.name"
                :value="hero.name"
              ></el-option>
            </el-select>
          </el-form-item>

          <!-- 自动接受交换位置 -->
          <el-form-item label="自动接受交换位置" prop="auto_accept_swap_position">
            <el-switch v-model="form.auto_accept_swap_position"></el-switch>
          </el-form-item>

          <!-- 自动接受交换英雄 -->
          <el-form-item label="自动接受交换英雄" prop="auto_accept_swap_champion">
            <el-switch v-model="form.auto_accept_swap_champion"></el-switch>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="onSubmit()">保存设置</el-button>
            <el-button @click="onReset()">重置</el-button>
          </el-form-item>
        </el-form>
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

// 表单引用
const formRef = ref(null)

// 表单数据 - 添加初始值对象
const form = reactive({
  auto_accept: false,
  auto_pick_champions: '',
  auto_ban_champions: '',
  auto_accept_swap_position: false,
  auto_accept_swap_champion: false,
})

// 英雄列表
const heroes = [
  { id: 1, name: '英雄A' },
  { id: 2, name: '英雄B' },
  { id: 3, name: '英雄C' },
  // 可根据需要添加更多英雄
]

// 提交表单
const onSubmit = async () => {
  try {
    const response = await axios.post('http://127.0.0.1:8000/api/user_settings/update_all', form)
    ElMessage({
      message: '设置已保存！',
      type: 'success'
    })
    console.log('Response from server:', response.data)
  } catch (error) {
    ElMessage({
      message: '保存失败，请稍后重试。',
      type: 'error'
    })
    console.error('Error sending settings to server:', error)
  }
}

// 重置表单
const onReset = () => {
  // 重置所有字段到初始值
  formRef.value.resetFields()
}
</script>

<style scoped>
.pre-game-setup {
  padding: 20px;
}

h2 {
  margin: 0;
}

.el-header {
  background-color: #f5f5f5;
  padding: 10px;
  text-align: center;
}
</style>