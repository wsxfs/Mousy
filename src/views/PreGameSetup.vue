<template>
  <div class="pre-game-setup">
    <el-container>
      <el-header>
        <h2>赛前预设</h2>
      </el-header>
      <el-main>
        <el-form :model="form" label-width="130px" ref="form">
          <!-- 自动接受对局 -->
          <el-form-item label="自动接受对局">
            <el-switch v-model="form.auto_accept"></el-switch>
          </el-form-item>

          <!-- 自动选择英雄 -->
          <el-form-item label="自动选择英雄">
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
          <el-form-item label="自动禁用英雄">
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
          <el-form-item label="自动接受交换位置">
            <el-switch v-model="form.auto_accept_swap_position"></el-switch>
          </el-form-item>

          <!-- 自动接受交换英雄 -->
          <el-form-item label="自动接受交换英雄">
            <el-switch v-model="form.auto_accept_swap_champion"></el-switch>
          </el-form-item>

          <el-form-item>
            <el-button type="primary" @click="onSubmit">保存设置</el-button>
            <el-button @click="onReset">重置</el-button>
          </el-form-item>
        </el-form>
      </el-main>
    </el-container>
  </div>
</template>


<script>
import axios from "axios";
export default {
  name: "PreGameSetup",
  data() {
    return {
      form: {
        auto_accept: false,
        auto_pick_champions: "",
        auto_ban_champions: "",
        auto_accept_swap_position: false,
        auto_accept_swap_champion: false,
      },
      heroes: [
        { id: 1, name: "英雄A" },
        { id: 2, name: "英雄B" },
        { id: 3, name: "英雄C" },
        // 可根据需要添加更多英雄
      ],
    };
  },
  methods: {
    async onSubmit() {
      try {
        const response = await axios.post("http://127.0.0.1:8000/api/user_settings/update_all", this.form);
        this.$message({
          message: "设置已保存！",
          type: "success",
        });
        console.log("Response from server:", response.data);
      } catch (error) {
        this.$message({
          message: "保存失败，请稍后重试。",
          type: "error",
        });
        console.error("Error sending settings to server:", error);
      }
    },
    onReset() {
      this.$refs.form.resetFields();
      this.$message({
        message: "设置已重置！",
        type: "info",
      });
    },
  },
};
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