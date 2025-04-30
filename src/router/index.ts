// router/index.ts
import { createRouter, createWebHashHistory } from 'vue-router';
import type { RouteRecordRaw } from 'vue-router';
import MainLayout from '../layouts/MainLayout.vue';
import EmptyLayout from '../layouts/EmptyLayout.vue';
import PreGameSetup from '../views/PreGameSetup/PreGameSetup.vue';
import MatchHistory from '../views/MatchHistory/MatchHistory.vue';
import MatchData from '../views/ChampionRanking/ChampionRanking.vue';
import HelloWorld from '../views/HelloWorld/HelloWorld.vue';
import GameAnalysis from '../views/GameAnalysis/GameAnalysis.vue'
import NoteBook from '../views/NoteBook/Notebook.vue'
import { useWebSocketStore } from '../stores/websocket'
import { ElMessage } from 'element-plus'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: MainLayout,
    redirect: '/hello',
    children: [
      { path: '/hello', name: 'HelloWorld', component: HelloWorld },
      { path: '/pregame', name: 'PreGameSetup', component: PreGameSetup },
      { path: '/match-history', name: 'MatchHistory', component: MatchHistory },
      { path: '/match-data', name: 'MatchData', component: MatchData },
      { path: '/game-analysis', name: 'GameAnalysis', component: GameAnalysis },
      { path: '/notebook', name: 'Notebook', component: NoteBook },
    ]
  },
  {
    path: '/champ-select',
    component: EmptyLayout,
    children: [
      {
        path: '',
        name: 'ChampSelect',
        component: () => import('../views/ChampSelectHelper/ChampSelectHelper.vue')
      }
    ]
  },
  {
    path: '/game-summary',
    component: EmptyLayout,
    children: [
      {
        path: '',
        name: 'GameSummary',
        component: () => import('../views/GameSummary/GameSummary.vue')
      }
    ]
  }
];

const router = createRouter({
  history: createWebHashHistory(),
  routes
});

// 添加全局前置守卫
router.beforeEach((to, from, next) => {
  const wsStore = useWebSocketStore()
  
  // 允许访问的路径
  const allowedPaths = ['/hello', '/champ-select']
  
  // 如果目标路径在允许列表中，直接放行
  if (allowedPaths.includes(to.path)) {
    next()
    return
  }
  
  // 检查LCU连接状态
  if (!wsStore.lcuConnected) {
    // 如果未连接，显示提示消息并重定向到HelloWorld页面
    ElMessage.warning('请先连接LCU后再访问此页面')
    // 使用replace而不是next来替换当前历史记录，避免回退时出现问题
    router.replace('/hello')
    return
  }
  
  // 如果已连接，允许访问
  next()
})

// 添加全局后置守卫，确保路由变化后侧边栏状态正确
router.afterEach((to) => {
  // 获取MainLayout组件实例
  const mainLayout = document.querySelector('.el-container')
  if (mainLayout) {
    // 触发自定义事件，通知侧边栏更新选中状态
    const event = new CustomEvent('route-changed', { detail: { path: to.path } })
    mainLayout.dispatchEvent(event)
  }
})

export default router;
