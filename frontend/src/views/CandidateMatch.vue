<template>
  <div class="match-page">
    <h2>📋 候选人匹配筛查</h2>

    <el-card class="input-card">
      <el-tabs v-model="inputMode">
        <el-tab-pane label="📝 直接输入文本" name="text">
          <el-form :model="textForm" label-width="100px">
            <el-form-item label="候选人姓名">
              <el-input v-model="textForm.candidate_name" placeholder="如：张三" />
            </el-form-item>
            <el-form-item label="岗位名称">
              <el-input v-model="textForm.job_title" placeholder="如：高级Java开发工程师" />
            </el-form-item>
            <el-form-item label="简历内容">
              <el-input v-model="textForm.resume_text" type="textarea" :rows="8"
                placeholder="粘贴候选人简历内容..." />
            </el-form-item>
            <el-form-item label="岗位JD">
              <el-input v-model="textForm.jd_text" type="textarea" :rows="8"
                placeholder="粘贴岗位JD内容..." />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="submitText" :loading="submitting">
                🚀 开始分析
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="📁 上传文件" name="file">
          <el-form :model="fileForm" label-width="100px">
            <el-form-item label="候选人姓名">
              <el-input v-model="fileForm.candidate_name" placeholder="如：张三" />
            </el-form-item>
            <el-form-item label="岗位名称">
              <el-input v-model="fileForm.job_title" placeholder="如：高级Java开发工程师" />
            </el-form-item>
            <el-form-item label="简历文件">
              <el-upload ref="resumeUpload" :auto-upload="false" :limit="1"
                accept=".txt,.md,.pdf,.docx" :on-change="(f) => fileForm.resume_file = f.raw">
                <el-button type="primary" plain>选择简历文件</el-button>
                <template #tip>
                  <div class="el-upload__tip">支持 txt / md，PDF和Word需安装解析库</div>
                </template>
              </el-upload>
            </el-form-item>
            <el-form-item label="JD文件">
              <el-upload ref="jdUpload" :auto-upload="false" :limit="1"
                accept=".txt,.md,.pdf,.docx" :on-change="(f) => fileForm.jd_file = f.raw">
                <el-button type="primary" plain>选择JD文件</el-button>
              </el-upload>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="submitFile" :loading="submitting">
                🚀 开始分析
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 提交成功提示 -->
    <el-card v-if="taskSubmitted" class="result-card">
      <el-result icon="success" title="任务已提交" :sub-title="`任务ID: ${taskId}，正在后台处理中...`">
        <template #extra>
          <el-button type="primary" @click="refreshReport">刷新查看结果</el-button>
        </template>
      </el-result>
    </el-card>

    <!-- 报告展示 -->
    <el-card v-if="report && report.status === 'done'" class="result-card">
      <template #header>
        <div class="report-header">
          <span>📊 评估报告 — {{ report.candidate_name }}（{{ report.job_title }}）</span>
          <el-tag v-if="report.match_score" :type="scoreTagType(report.match_score)" size="large">
            综合匹配度：{{ report.match_score.toFixed(1) }} / 5
          </el-tag>
        </div>
      </template>

      <!-- 硬性条件 -->
      <el-collapse>
        <el-collapse-item title="✅ 硬性条件校验" name="hard">
          <el-table :data="report.hard_check" stripe size="small">
            <el-table-column prop="item" label="校验项" width="140" />
            <el-table-column prop="requirement" label="JD要求" />
            <el-table-column prop="candidate_status" label="候选人情况" />
            <el-table-column prop="result" label="结果" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.result === '达标'" type="success">✅ 达标</el-tag>
                <el-tag v-else-if="row.result === '不达标'" type="danger">❌ 不达标</el-tag>
                <el-tag v-else type="warning">⚠️ 存疑</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="detail" label="说明" />
          </el-table>
        </el-collapse-item>

        <!-- 技能匹配 -->
        <el-collapse-item title="⭐ 技能匹配详情" name="match">
          <el-table :data="report.match_detail" stripe size="small">
            <el-table-column prop="dimension" label="评分维度" width="160" />
            <el-table-column prop="score" label="分数" width="100">
              <template #default="{ row }">
                <el-rate :model-value="row.score" disabled show-score text-color="#ff9900" />
              </template>
            </el-table-column>
            <el-table-column prop="reason" label="评分依据" />
            <el-table-column prop="evidence" label="简历证据" />
          </el-table>
        </el-collapse-item>

        <!-- 风险项 -->
        <el-collapse-item title="⚠️ 风险提示" name="risk">
          <el-table :data="report.risks" stripe size="small">
            <el-table-column prop="type" label="风险类型" width="140" />
            <el-table-column prop="level" label="等级" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.level === '高'" type="danger">🔴 高风险</el-tag>
                <el-tag v-else-if="row.level === '中'" type="warning">🟡 中风险</el-tag>
                <el-tag v-else type="success">🟢 低风险</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="description" label="描述" />
            <el-table-column prop="suggestion" label="建议" />
          </el-table>
        </el-collapse-item>

        <!-- 完整报告 -->
        <el-collapse-item title="📄 完整报告" name="full">
          <div class="markdown-body" v-html="renderedReport"></div>
        </el-collapse-item>
      </el-collapse>
    </el-card>

    <!-- 失败提示 -->
    <el-card v-if="report && report.status === 'failed'" class="result-card">
      <el-result icon="error" title="评估失败" :sub-title="report.error_message" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import { submitMatch, uploadMatch, getMatchReport } from '../api/match'

const inputMode = ref('text')
const submitting = ref(false)
const taskSubmitted = ref(false)
const taskId = ref(null)
const report = ref(null)
let pollTimer = null

const textForm = ref({ candidate_name: '', job_title: '', resume_text: '', jd_text: '' })
const fileForm = ref({ candidate_name: '', job_title: '', resume_file: null, jd_file: null })

async function submitText() {
  if (!textForm.value.candidate_name || !textForm.value.resume_text || !textForm.value.jd_text) {
    ElMessage.warning('请填写完整信息')
    return
  }
  submitting.value = true
  try {
    const { data } = await submitMatch(textForm.value)
    taskId.value = data.task_id
    taskSubmitted.value = true
    ElMessage.success('任务已提交')
    startPolling()
  } finally {
    submitting.value = false
  }
}

async function submitFile() {
  if (!fileForm.value.candidate_name || !fileForm.value.resume_file || !fileForm.value.jd_file) {
    ElMessage.warning('请填写完整信息并选择文件')
    return
  }
  submitting.value = true
  try {
    const fd = new FormData()
    fd.append('candidate_name', fileForm.value.candidate_name)
    fd.append('job_title', fileForm.value.job_title)
    fd.append('resume_file', fileForm.value.resume_file)
    fd.append('jd_file', fileForm.value.jd_file)
    const { data } = await uploadMatch(fd)
    taskId.value = data.task_id
    taskSubmitted.value = true
    ElMessage.success('文件上传并提交成功')
    startPolling()
  } finally {
    submitting.value = false
  }
}

function startPolling() {
  clearInterval(pollTimer)
  pollTimer = setInterval(async () => {
    try {
      const { data } = await getMatchReport(taskId.value)
      if (data.status === 'done' || data.status === 'failed') {
        clearInterval(pollTimer)
        report.value = data
      }
    } catch { /* 忽略轮询错误 */ }
  }, 2000)
}

function refreshReport() {
  getMatchReport(taskId.value).then(({ data }) => {
    report.value = data
    if (data.status === 'done' || data.status === 'failed') {
      clearInterval(pollTimer)
    }
  })
}

function scoreTagType(score) {
  if (score >= 4) return 'success'
  if (score >= 3) return 'warning'
  return 'danger'
}

const renderedReport = computed(() => {
  if (!report.value?.full_report) return ''
  return marked.parse(report.value.full_report)
})
</script>

<style scoped>
.match-page { max-width: 1000px; margin: 0 auto; }
.input-card { margin-bottom: 20px; }
.result-card { margin-bottom: 20px; }
.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

<!-- v-html 渲染的 Markdown 内容需要非 scoped 样式 -->
<style>
.markdown-body { padding: 16px; line-height: 1.8; color: #303133; }
.markdown-body h1 { font-size: 24px !important; font-weight: 700 !important; margin: 16px 0 12px !important; border-bottom: 2px solid #409EFF !important; padding-bottom: 8px !important; display: block !important; }
.markdown-body h2 { font-size: 20px !important; font-weight: 600 !important; margin: 14px 0 10px !important; border-bottom: 1px solid #dcdfe6 !important; padding-bottom: 6px !important; display: block !important; }
.markdown-body h3 { font-size: 17px !important; font-weight: 600 !important; margin: 12px 0 8px !important; display: block !important; }
.markdown-body p { margin: 8px 0 !important; }
.markdown-body strong { color: #303133 !important; font-weight: 700 !important; }
.markdown-body table { width: 100% !important; border-collapse: collapse !important; margin: 12px 0 !important; font-size: 14px !important; display: table !important; border: 1px solid #dcdfe6 !important; }
.markdown-body th { background: #f5f7fa !important; font-weight: 600 !important; padding: 8px 12px !important; border: 1px solid #dcdfe6 !important; text-align: left !important; }
.markdown-body td { padding: 8px 12px !important; border: 1px solid #dcdfe6 !important; }
.markdown-body tr:nth-child(even) { background: #fafafa !important; }
.markdown-body ul, .markdown-body ol { padding-left: 24px !important; margin: 8px 0 !important; }
.markdown-body li { margin: 4px 0 !important; }
.markdown-body hr { border: none !important; border-top: 1px solid #e4e7ed !important; margin: 16px 0 !important; }
.markdown-body code { background: #f0f2f5 !important; padding: 2px 6px !important; border-radius: 4px !important; font-size: 13px !important; }
.markdown-body pre { background: #f5f7fa !important; padding: 12px !important; border-radius: 6px !important; overflow-x: auto !important; }
.markdown-body pre code { background: none !important; padding: 0 !important; }
.markdown-body blockquote { border-left: 4px solid #409EFF !important; padding: 8px 16px !important; margin: 12px 0 !important; background: #ecf5ff !important; }
</style>
