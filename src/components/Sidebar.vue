<template>
    <el-menu default-active="1" class="el-menu-vertical-demo" :collapse="isCollapse" @open="handleOpen"
        @close="handleClose" @mouseenter="isCollapse = false" @mouseleave="isCollapse = true"  router >

        <el-menu-item index="1">
            <el-icon>
                <HomeFilled />
            </el-icon>
            <span>用户主页</span>
        </el-menu-item>

        <el-menu-item index="2">
            <el-icon>
                <Location />
            </el-icon>
            <span>赛前预设</span>
        </el-menu-item>

        <el-menu-item index="3">
            <el-icon>
                <Search />
            </el-icon>
            <span>战绩查询</span>
        </el-menu-item>

        <el-menu-item index="4">
            <el-icon>
                <document />
            </el-icon>
            <span>对战资料</span>
        </el-menu-item>

    </el-menu>
</template>

<script lang="ts" setup>
import { HomeFilled, Location, Search, Document } from '@element-plus/icons-vue'
import { ref } from 'vue'

const isCollapse = ref(true)

const handleOpen = (key: string, keyPath: string[]) => {
    console.log(`Opened: ${key}`, keyPath)
}
const handleClose = (key: string, keyPath: string[]) => {
    console.log(`Closed: ${key}`, keyPath)
}
</script>

<style scoped>
.el-menu-vertical-demo {
    position: absolute; /* 绝对定位使其能够超出容器 */
    height: 100%;
}
</style>