<template>
  <div class="interview-page">
    <h2>🎯 面试一致性评估</h2>

    <el-card class="input-card">
      <el-tabs v-model="inputMode">
        <el-tab-pane label="📝 直接输入文本" name="text">
          <el-form :model="textForm" label-width="120px">
            <el-form-item label="候选人姓名">
              <el-input v-model="textForm.candidate_name" placeholder="如：张三" />
            </el-form-item>
            <el-form-item label="岗位名称">
              <el-input v-model="textForm.job_title" placeholder="如：高级Java开发工程师" />
            </el-form-item>
            <el-form-item label="能力模型">
              <el-input v-model="textForm.competency_model_text" type="textarea" :rows="8"
                placeholder="粘贴岗位能力模型..." />
            </el-form-item>
            <el-form-item label="面试记录">
              <el-input v-model="textForm.interview_records_text" type="textarea" :rows="10"
                placeholder="粘贴多轮面试记录（用【第N轮】分隔）..." />
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="submitText" :loading="submitting">
                🚀 开始评估
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <el-tab-pane label="📁 上传文件" name="file">
          <el-form :model="fileForm" label-width="120px">
            <el-form-item label="候选人姓名">
              <el-input v-model="fileForm.candidate_name" placeholder="如：张三" />
            </el-form-item>
            <el-form-item label="岗位名称">
              <el-input v-model="fileForm.job_title" placeholder="如：高级Java开发工程师" />
            </el-form-item>
            <el-form-item label="能力模型文件">
              <el-upload ref="compUpload" :auto-upload="false" :limit="1"
                accept=".txt,.md" :on-change="(f) => fileForm.competency_file = f.raw">
                <el-button type="primary" plain>选择能力模型文件</el-button>
              </el-upload>
            </el-form-item>
            <el-form-item label="面试记录文件">
              <el-upload ref="interviewUpload" :auto-upload="false" multiple
                accept=".txt,.md" :on-change="handleInterviewFiles">
                <el-button type="primary" plain>选择面试记录文件（可多选）</el-button>
                <template #tip>
                  <div class="el-upload__tip">可选择多轮面试记录文件，每个文件对应一轮</div>
                </template>
              </el-upload>
            </el-form-item>
            <el-form-item>
              <el-button type="primary" @click="submitFile" :loading="submitting">
                🚀 开始评估
              </el-button>
            </el-form-item>
          </el-form>
        </el-tab-pane>
      </el-tabs>
    </el-card>

    <!-- 提交成功 -->
    <el-card v-if="taskSubmitted && !report" class="result-card">
      <el-result icon="success" title="任务已提交" :sub-title="`任务ID: ${taskId}，正在分析中...`">
        <template #extra>
          <el-button type="primary" @click="refreshReport">刷新查看结果</el-button>
        </template>
      </el-result>
    </el-card>

    <!-- 报告 -->
    <el-card v-if="report && report.status === 'done'" class="result-card">
      <template #header>
        <div class="report-header">
          <span>📊 面试一致性报告 — {{ report.candidate_name }}</span>
          <el-tag v-if="report.consensus_level" :type="consensusTagType(report.consensus_level)" size="large">
            结论一致性：{{ report.consensus_level }}
          </el-tag>
        </div>
      </template>

      <el-collapse>
        <!-- 评分偏差 -->
        <el-collapse-item title="📐 评分偏差分析" name="deviation">
          <el-table :data="report.deviation" stripe size="small">
            <el-table-column prop="dimension" label="维度" width="140" />
            <el-table-column prop="weight" label="权重" width="80">
              <template #default="{ row }">{{ (row.weight * 100).toFixed(0) }}%</template>
            </el-table-column>
            <el-table-column label="各轮评分" width="200">
              <template #default="{ row }">
                <span v-for="(score, round, idx) in row.scores" :key="round">
                  {{ round }}: <strong>{{ score ?? '未评' }}</strong>
                  <span v-if="idx < Object.keys(row.scores).length - 1"> | </span>
                </span>
              </template>
            </el-table-column>
            <el-table-column prop="max_gap" label="最大分差" width="100" />
            <el-table-column prop="deviation_level" label="偏差等级" width="120">
              <template #default="{ row }">
                <el-tag v-if="row.deviation_level === '严重偏差'" type="danger">🔴 {{ row.deviation_level }}</el-tag>
                <el-tag v-else-if="row.deviation_level === '轻微偏差'" type="warning">⚠️ {{ row.deviation_level }}</el-tag>
                <el-tag v-else type="success">✅ {{ row.deviation_level }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="analysis" label="分析" />
          </el-table>
        </el-collapse-item>

        <!-- 证据充分性 -->
        <el-collapse-item title="🔍 证据充分性" name="evidence">
          <div v-for="item in report.evidence" :key="item.interviewer" class="evidence-item">
            <h4>{{ item.interviewer }} —
              <el-tag :type="item.overall_quality === '充分' ? 'success' : item.overall_quality === '一般' ? 'warning' : 'danger'" size="small">
                {{ item.overall_quality }}
              </el-tag>
              <span class="weak-hint">（{{ item.weak_count }}项证据不足）</span>
            </h4>
            <el-table :data="item.details" stripe size="small">
              <el-table-column prop="dimension" label="维度" width="140" />
              <el-table-column prop="score" label="评分" width="80" />
              <el-table-column prop="evidence_in_record" label="记录中的证据" />
              <el-table-column prop="evidence_level" label="证据等级" width="100" />
              <el-table-column prop="issue" label="问题" />
            </el-table>
          </div>
        </el-collapse-item>

        <!-- 追问遗漏 -->
        <el-collapse-item title="❓ 追问遗漏" name="missed">
          <el-table :data="report.missed_followups" stripe size="small">
            <el-table-column prop="interview_round" label="面试轮次" width="120" />
            <el-table-column prop="context" label="当时上下文" />
            <el-table-column prop="should_ask" label="应该追问" />
            <el-table-column prop="severity" label="严重程度" width="100">
              <template #default="{ row }">
                <el-tag v-if="row.severity === '严重'" type="danger">严重</el-tag>
                <el-tag v-else-if="row.severity === '中等'" type="warning">中等</el-tag>
                <el-tag v-else type="info">轻微</el-tag>
              </template>
            </el-table-column>
          </el-table>
        </el-collapse-item>

        <!-- 完整报告 -->
        <el-collapse-item title="📄 完整报告" name="full">
          <div class="markdown-body" v-html="renderedReport"></div>
        </el-collapse-item>
      </el-collapse>
    </el-card>

    <!-- 失败 -->
    <el-card v-if="report && report.status === 'failed'" class="result-card">
      <el-result icon="error" title="评估失败" :sub-title="report.error_message" />
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { marked } from 'marked'
import { submitInterview, uploadInterview, getInterviewReport } from '../api/interview'

const inputMode = ref('text')
const submitting = ref(false)
const taskSubmitted = ref(false)
const taskId = ref(null)
const report = ref(null)
let pollTimer = null

const textForm = ref({
  candidate_name: '', job_title: '',
  competency_model_text: '', interview_records_text: ''
})

const fileForm = ref({
  candidate_name: '', job_title: '',
  competency_file: null, interview_files: []
})

function handleInterviewFiles(file) {
  // 累积多文件
  if (!fileForm.value.interview_files) fileForm.value.interview_files = []
  fileForm.value.interview_files.push(file.raw)
}

async function submitText() {
  if (!textForm.value.candidate_name || !textForm.value.competency_model_text || !textForm.value.interview_records_text) {
    ElMessage.warning('请填写完整信息')
    return
  }
  submitting.value = true
  try {
    const { data } = await submitInterview(textForm.value)
    taskId.value = data.task_id
    taskSubmitted.value = true
    startPolling()
  } finally {
    submitting.value = false
  }
}

async function submitFile() {
  if (!fileForm.value.candidate_name || !fileForm.value.competency_file || !fileForm.value.interview_files?.length) {
    ElMessage.warning('请填写完整信息并选择文件')
    return
  }
  submitting.value = true
  try {
    const fd = new FormData()
    fd.append('candidate_name', fileForm.value.candidate_name)
    fd.append('job_title', fileForm.value.job_title)
    fd.append('competency_file', fileForm.value.competency_file)
    fileForm.value.interview_files.forEach(f => fd.append('interview_files', f))
    const { data } = await uploadInterview(fd)
    taskId.value = data.task_id
    taskSubmitted.value = true
    startPolling()
  } finally {
    submitting.value = false
  }
}

function startPolling() {
  clearInterval(pollTimer)
  pollTimer = setInterval(async () => {
    try {
      const { data } = await getInterviewReport(taskId.value)
      if (data.status === 'done' || data.status === 'failed') {
        clearInterval(pollTimer)
        report.value = data
      }
    } catch { /* ignore */ }
  }, 2000)
}

function refreshReport() {
  getInterviewReport(taskId.value).then(({ data }) => {
    report.value = data
    if (data.status === 'done' || data.status === 'failed') {
      clearInterval(pollTimer)
    }
  })
}

function consensusTagType(level) {
  if (level === '一致' || level === '基本一致') return 'success'
  if (level === '存在分歧') return 'warning'
  return 'danger'
}

const renderedReport = computed(() => {
  if (!report.value?.full_report) return ''
  return marked.parse(report.value.full_report)
})
</script>

<style scoped>
.interview-page { max-width: 1000px; margin: 0 auto; }
.input-card { margin-bottom: 20px; }
.result-card { margin-bottom: 20px; }
.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.evidence-item {
  margin-bottom: 20px;
  padding: 12px;
  background: #fafafa;
  border-radius: 8px;
}
.evidence-item h4 { margin-bottom: 8px; }
.weak-hint { color: #909399; font-size: 13px; margin-left: 8px; }
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
