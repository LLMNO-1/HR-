// ==== 新增：Dashboard 统计 API 封装 ====
// 调用后端 GET /api/v1/dashboard/stats 获取首页统计数据
import api from './index'

/** 获取 Dashboard 首页统计数据 */
export function getDashboardStats() {
  return api.get('/dashboard/stats')
}
