import api from './index'

/** 提交候选人匹配评估（JSON模式） */
export function submitMatch(data) {
  return api.post('/match/evaluate', data)
}

/** 上传文件并提交评估 */
export function uploadMatch(formData) {
  return api.post('/match/evaluate/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/** 查询匹配评估历史列表 */
export function getMatchReports(skip = 0, limit = 20) {
  return api.get('/match/reports', { params: { skip, limit } })
}

/** 查询单份匹配评估报告 */
export function getMatchReport(id) {
  return api.get(`/match/reports/${id}`)
}
