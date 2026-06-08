import api from './index'

/** 提交面试一致性评估（JSON模式） */
export function submitInterview(data) {
  return api.post('/interview/evaluate', data)
}

/** 上传文件并提交评估 */
export function uploadInterview(formData) {
  return api.post('/interview/evaluate/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' }
  })
}

/** 查询面试评估历史列表 */
export function getInterviewReports(skip = 0, limit = 20) {
  return api.get('/interview/reports', { params: { skip, limit } })
}

/** 查询单份面试评估报告 */
export function getInterviewReport(id) {
  return api.get(`/interview/reports/${id}`)
}
