// router/index.ts
import { createRouter, createWebHistory } from 'vue-router';
import UserHome from '../views/UserHome.vue';
import PreGameSetup from '../views/PreGameSetup.vue';
import MatchHistory from '../views/MatchHistory.vue';
import MatchData from '../views/MatchData.vue';
import HelloWorld from '../views/HelloWorld.vue';

const routes = [
  { path: '/', redirect: '/home' },
  { path: '/home', name: 'UserHome', component: UserHome },
  { path: '/pregame', name: 'PreGameSetup', component: PreGameSetup },
  { path: '/match-history', name: 'MatchHistory', component: MatchHistory },
  { path: '/match-data', name: 'MatchData', component: MatchData },
  { path: '/hello', name: 'HelloWorld', component: HelloWorld },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

export default router;
