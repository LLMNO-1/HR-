import { createRouter, createWebHistory } from 'vue-router'

const routes = [
  {
    path: '/',
    redirect: '/match'
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
