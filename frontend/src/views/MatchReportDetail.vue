<template>
  <div class="report-detail">
    <el-page-header @back="$router.back()" title="返回">
      <template #content>
        <span>候选人匹配报告 #{{ reportId }}</span>
      </template>
    </el-page-header>

    <div v-loading="loading" style="margin-top: 20px;">
      <el-card v-if="report">
        <template #header>
          <div class="report-header">
            <span>📊 {{ report.candidate_name }} — {{ report.job_title }}</span>
            <el-tag :type="scoreTag(report.match_score)" size="large">
              综合匹配度：{{ report.match_score?.toFixed(1) ?? '-' }} / 5
            </el-tag>
          </div>
        </template>

        <el-descriptions :column="2" border>
          <el-descriptions-item label="候选人">{{ report.candidate_name }}</el-descriptions-item>
          <el-descriptions-item label="岗位">{{ report.job_title }}</el-descriptions-item>
          <el-descriptions-item label="处理耗时">{{ report.duration_ms ? report.duration_ms + 'ms' : '-' }}</el-descriptions-item>
          <el-descriptions-item label="状态">
            <el-tag :type="report.status === 'done' ? 'success' : 'danger'">{{ report.status }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>

        <div v-if="report.full_report" class="report-content">
          <h3>📄 完整报告</h3>
          <div class="markdown-body" v-html="marked.parse(report.full_report)"></div>
        </div>
      </el-card>

      <el-empty v-if="!loading && !report" description="报告不存在" />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { marked } from 'marked'
import { getMatchReport } from '../api/match'

const route = useRoute()
const reportId = route.params.id
const report = ref(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const { data } = await getMatchReport(reportId)
    report.value = data
  } finally {
    loading.value = false
  }
})

function scoreTag(score) {
  if (!score) return 'info'
  if (score >= 4) return 'success'
  if (score >= 3) return 'warning'
  return 'danger'
}
</script>

<style scoped>
.report-detail { max-width: 900px; margin: 0 auto; }
.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.report-content { margin-top: 24px; }
</style>

<style>
.markdown-body { padding: 16px; line-height: 1.8; background: #fafafa; border-radius: 8px; color: #303133; }
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
