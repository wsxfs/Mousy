// router/index.ts
import { createRouter, createWebHashHistory } from 'vue-router';
import UserHome from '../views/UserHome/UserHome.vue';
import PreGameSetup from '../views/PreGameSetup/PreGameSetup.vue';
import MatchHistory from '../views/MatchHistory/MatchHistory.vue';
import MatchData from '../views/ChampionRanking/ChampionRanking.vue';
import HelloWorld from '../views/HelloWorld/HelloWorld.vue';

const routes = [
  { path: '/', redirect: '/hello' },
  { path: '/hello', name: 'HelloWorld', component: HelloWorld },
  { path: '/home', name: 'UserHome', component: UserHome },
  { path: '/pregame', name: 'PreGameSetup', component: PreGameSetup },
  { path: '/match-history', name: 'MatchHistory', component: MatchHistory },
  { path: '/match-data', name: 'MatchData', component: MatchData },
];

const router = createRouter({
  history: createWebHashHistory(),
  routes,
});

export default router;
