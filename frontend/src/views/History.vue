<template>
  <div class="history-page">
    <h2>📋 历史记录</h2>

    <el-tabs v-model="activeTab">
      <el-tab-pane label="候选人匹配筛查" name="match">
        <el-table :data="matchReports" stripe v-loading="matchLoading">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="candidate_name" label="候选人" width="120" />
          <el-table-column prop="job_title" label="岗位" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.status === 'done'" type="success">✅ 完成</el-tag>
              <el-tag v-else-if="row.status === 'processing'" type="warning">⏳ 处理中</el-tag>
              <el-tag v-else-if="row.status === 'pending'" type="info">等待中</el-tag>
              <el-tag v-else type="danger">❌ 失败</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="match_score" label="匹配度" width="100">
            <template #default="{ row }">
              <span v-if="row.match_score">{{ row.match_score.toFixed(1) }} / 5</span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              {{ new Date(row.created_at).toLocaleString('zh-CN') }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button type="primary" link @click="$router.push(`/match/report/${row.id}`)">
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="面试一致性评估" name="interview">
        <el-table :data="interviewReports" stripe v-loading="interviewLoading">
          <el-table-column prop="id" label="ID" width="60" />
          <el-table-column prop="candidate_name" label="候选人" width="120" />
          <el-table-column prop="job_title" label="岗位" />
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag v-if="row.status === 'done'" type="success">✅ 完成</el-tag>
              <el-tag v-else-if="row.status === 'processing'" type="warning">⏳ 处理中</el-tag>
              <el-tag v-else-if="row.status === 'pending'" type="info">等待中</el-tag>
              <el-tag v-else type="danger">❌ 失败</el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="consensus_level" label="结论一致性" width="120">
            <template #default="{ row }">
              <span v-if="row.consensus_level">{{ row.consensus_level }}</span>
              <span v-else>-</span>
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              {{ new Date(row.created_at).toLocaleString('zh-CN') }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="120">
            <template #default="{ row }">
              <el-button type="primary" link @click="$router.push(`/interview/report/${row.id}`)">
                查看详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { getMatchReports } from '../api/match'
import { getInterviewReports } from '../api/interview'

const activeTab = ref('match')
const matchReports = ref([])
const interviewReports = ref([])
const matchLoading = ref(false)
const interviewLoading = ref(false)

onMounted(() => {
  loadMatchReports()
  loadInterviewReports()
})

async function loadMatchReports() {
  matchLoading.value = true
  try {
    const { data } = await getMatchReports()
    matchReports.value = data
  } finally {
    matchLoading.value = false
  }
}

async function loadInterviewReports() {
  interviewLoading.value = true
  try {
    const { data } = await getInterviewReports()
    interviewReports.value = data
  } finally {
    interviewLoading.value = false
  }
}
</script>

<style scoped>
.history-page { max-width: 1000px; margin: 0 auto; }
</style>
