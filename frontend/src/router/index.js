import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/dashboard'  // 修改：根路径跳转到新增的 Dashboard 首页
  },
  {  // 新增：数据概览 Dashboard 首页路由
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('../views/Dashboard.vue')
  },
  {
    path: '/match',
    name: 'CandidateMatch',
    component: () => import('../views/CandidateMatch.vue')
  },
  {
    path: '/interview',
    name: 'InterviewEval',
    component: () => import('../views/InterviewEval.vue')
  },
  {
    path: '/history',
    name: 'History',
    component: () => import('../views/History.vue')
  },
  {
    path: '/match/report/:id',
    name: 'MatchReportDetail',
    component: () => import('../views/MatchReportDetail.vue')
  },
  {
    path: '/interview/report/:id',
    name: 'InterviewReportDetail',
    component: () => import('../views/InterviewReportDetail.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
