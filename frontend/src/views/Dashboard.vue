<!--
==== 新增：Dashboard 首页数据概览 ====
展示评估统计卡片 + ECharts 图表（状态分布饼图、月度趋势折线图）
依赖：Element Plus（el-card/el-row/el-col）+ vue-echarts（图表）
数据来源：GET /api/v1/dashboard/stats
-->
<template>
  <div class="dashboard-page">
    <h2>📊 数据概览</h2>

    <!-- 加载中占位 -->
    <div v-if="loading" class="loading-placeholder">
      <el-skeleton :rows="3" animated />
    </div>

    <!-- ===== 统计卡片行 ===== -->
    <el-row v-else :gutter="20" class="stats-row">
      <!-- 卡片1：匹配筛查总览 -->
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-card--match">
          <div class="stat-label">匹配筛查</div>
          <div class="stat-value">{{ stats.match.total }}</div>
          <div class="stat-detail">
            <span class="done">✅ {{ stats.match.done }}</span>
            <span class="processing" v-if="stats.match.processing">⏳ {{ stats.match.processing }}</span>
            <span class="failed" v-if="stats.match.failed">❌ {{ stats.match.failed }}</span>
          </div>
        </el-card>
      </el-col>

      <!-- 卡片2：面试评估总览 -->
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-card--interview">
          <div class="stat-label">面试评估</div>
          <div class="stat-value">{{ stats.interview.total }}</div>
          <div class="stat-detail">
            <span class="done">✅ {{ stats.interview.done }}</span>
            <span class="processing" v-if="stats.interview.processing">⏳ {{ stats.interview.processing }}</span>
            <span class="failed" v-if="stats.interview.failed">❌ {{ stats.interview.failed }}</span>
          </div>
        </el-card>
      </el-col>

      <!-- 卡片3：平均匹配分 -->
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-card--score">
          <div class="stat-label">平均匹配分</div>
          <!-- avg_score 可能为 null（无已完成报告时显示 "-"） -->
          <div class="stat-value">{{ stats.match.avg_score != null ? stats.match.avg_score.toFixed(1) : '-' }}</div>
          <div class="stat-unit">满分 5.0</div>
        </el-card>
      </el-col>

      <!-- 卡片4：总评估量 -->
      <el-col :span="6">
        <el-card shadow="hover" class="stat-card stat-card--total">
          <div class="stat-label">总评估量</div>
          <div class="stat-value">{{ stats.match.total + stats.interview.total }}</div>
          <div class="stat-unit">匹配 + 面试</div>
        </el-card>
      </el-col>
    </el-row>

    <!-- ===== 图表行 ===== -->
    <el-row v-if="!loading" :gutter="20" class="charts-row">
      <!-- 左列：匹配状态分布 + 月度趋势 -->
      <el-col :span="12">
        <!-- 饼图1：匹配评估状态分布 -->
        <el-card shadow="hover" class="chart-card">
          <template #header><span>匹配评估状态分布</span></template>
          <!-- v-chart 是 vue-echarts 组件，option 传入 ECharts 配置对象 -->
          <!-- autoresize 让图表随容器自适应大小 -->
          <v-chart :option="matchStatusOption" autoresize style="height: 260px" />
        </el-card>
      </el-col>

      <!-- 右列：面试一致性分布 -->
      <el-col :span="12">
        <!-- 饼图2：面试一致性结论分布 -->
        <el-card shadow="hover" class="chart-card">
          <template #header><span>面试一致性结论分布</span></template>
          <v-chart :option="consensusOption" autoresize style="height: 260px" />
        </el-card>
      </el-col>
    </el-row>

    <!-- 第二行：月度趋势（独占一行，更宽） -->
    <el-row v-if="!loading" :gutter="20" class="charts-row">
      <el-col :span="24">
        <el-card shadow="hover" class="chart-card">
          <template #header><span>近6个月评估趋势</span></template>
          <v-chart :option="trendOption" autoresize style="height: 300px" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
/**
 * Dashboard 首页 —— 数据统计与可视化
 * 
 * 核心逻辑：
 * 1. onMounted 时调用 getDashboardStats() 获取后端聚合数据
 * 2. 将数据转换为 ECharts option 配置，传给 v-chart 渲染
 * 3. 颜色方案使用 Element Plus 主题色 #409EFF 及语义色（绿=完成、橙=处理中、红=失败）
 */
import { ref, computed, onMounted } from 'vue'
// vue-echarts 的 Vue3 组件（v-chart），已在 package.json 中安装
import VChart from 'vue-echarts'
// 按需引入 ECharts 核心和所需图表类型，避免全量打包
import { use } from 'echarts/core'
import { PieChart, BarChart, LineChart } from 'echarts/charts'
import { TitleComponent, TooltipComponent, LegendComponent, GridComponent } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { getDashboardStats } from '../api/dashboard'

// 注册 ECharts 组件（只注册用到的，Tree-shaking 优化包体积）
use([PieChart, BarChart, LineChart, TitleComponent, TooltipComponent, LegendComponent, GridComponent, CanvasRenderer])

const loading = ref(true)
// stats 原始数据，来自后端 DashboardStats 模型
const stats = ref({
  match: { total: 0, done: 0, processing: 0, failed: 0, avg_score: null },
  interview: { total: 0, done: 0, processing: 0, failed: 0, consensus_一致: 0, consensus_基本一致: 0, consensus_存在分歧: 0, consensus_严重分歧: 0 },
  monthly_trend: [],
})

// ---- ECharts 配置（computed，数据变化自动更新图表） ----

/** 
 * 饼图：匹配评估状态分布
 * 数据项：已完成(done) / 处理中(processing) / 失败(failed)
 * 颜色：绿 / 橙 / 红，对应 Element Plus 的 success/warning/danger 语义
 */
const matchStatusOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} 份 ({d}%)' },
  legend: { bottom: 0 },
  series: [{
    type: 'pie',
    radius: ['45%', '70%'],  // 环形饼图（空心），比实心更现代
    center: ['50%', '45%'],
    avoidLabelOverlap: false,
    label: { show: true, formatter: '{b}\n{c} 份' },
    data: [
      { value: stats.value.match.done, name: '已完成', itemStyle: { color: '#67C23A' } },
      { value: stats.value.match.processing, name: '处理中', itemStyle: { color: '#E6A23C' } },
      { value: stats.value.match.failed, name: '失败', itemStyle: { color: '#F56C6C' } },
    ].filter(d => d.value > 0),  // 值为0的项不显示（避免空扇区）
  }],
}))

/**
 * 饼图：面试一致性结论分布
 * 四档：一致 / 基本一致 / 存在分歧 / 严重分歧
 * 颜色从绿到红渐变，表达严重程度
 */
const consensusOption = computed(() => ({
  tooltip: { trigger: 'item', formatter: '{b}: {c} 份 ({d}%)' },
  legend: { bottom: 0 },
  series: [{
    type: 'pie',
    radius: ['45%', '70%'],
    center: ['50%', '45%'],
    label: { show: true, formatter: '{b}\n{c} 份' },
    data: [
      { value: stats.value.interview.consensus_一致, name: '一致', itemStyle: { color: '#67C23A' } },
      { value: stats.value.interview.consensus_基本一致, name: '基本一致', itemStyle: { color: '#409EFF' } },
      { value: stats.value.interview.consensus_存在分歧, name: '存在分歧', itemStyle: { color: '#E6A23C' } },
      { value: stats.value.interview.consensus_严重分歧, name: '严重分歧', itemStyle: { color: '#F56C6C' } },
    ].filter(d => d.value > 0),
  }],
}))

/**
 * 折线图：近6个月评估趋势
 * 双折线：蓝色=匹配筛查，绿色=面试评估
 * X轴为月份（如 "2026-03"），Y轴为数量
 */
const trendOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  legend: { data: ['匹配筛查', '面试评估'], bottom: 0 },
  grid: { left: '3%', right: '4%', bottom: '15%', containLabel: true },
  xAxis: {
    type: 'category',
    // 提取月份数组作为 X 轴标签
    data: stats.value.monthly_trend.map(t => t.month),
    axisLabel: { rotate: 0 },
  },
  yAxis: {
    type: 'value',
    // minInterval: 1 保证 Y 轴刻度为整数（评估数量不会出现小数）
    minInterval: 1,
  },
  series: [
    {
      name: '匹配筛查',
      type: 'line',
      data: stats.value.monthly_trend.map(t => t.match_count),
      smooth: true,              // 平滑曲线
      itemStyle: { color: '#409EFF' },
      areaStyle: { opacity: 0.1 },  // 半透明填充区域，更美观
    },
    {
      name: '面试评估',
      type: 'line',
      data: stats.value.monthly_trend.map(t => t.interview_count),
      smooth: true,
      itemStyle: { color: '#67C23A' },
      areaStyle: { opacity: 0.1 },
    },
  ],
}))

// 页面加载时请求数据
onMounted(async () => {
  try {
    const { data } = await getDashboardStats()
    stats.value = data
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
/* Dashboard 页面容器 */
.dashboard-page {
  max-width: 1200px;
  margin: 0 auto;
}
.dashboard-page h2 {
  margin-bottom: 20px;
  color: #303133;
}

/* 加载占位 */
.loading-placeholder {
  padding: 20px;
}

/* 统计卡片行 */
.stats-row {
  margin-bottom: 20px;
}

/* 每张统计卡片通用样式 */
.stat-card {
  text-align: center;
  border-radius: 8px;
}
.stat-card .stat-label {
  font-size: 14px;
  color: #909399;
  margin-bottom: 8px;
}
.stat-card .stat-value {
  font-size: 36px;
  font-weight: bold;
  color: #303133;
}
.stat-card .stat-detail {
  margin-top: 8px;
  font-size: 13px;
}
.stat-card .stat-unit {
  font-size: 12px;
  color: #C0C4CC;
  margin-top: 4px;
}

/* 详情行内各状态标记 */
.stat-detail .done     { color: #67C23A; margin: 0 4px; }
.stat-detail .processing { color: #E6A23C; margin: 0 4px; }
.stat-detail .failed   { color: #F56C6C; margin: 0 4px; }

/* 各卡片左侧彩色边框（用 border-top 做语义色区分） */
.stat-card--match    { border-top: 3px solid #409EFF; }
.stat-card--interview { border-top: 3px solid #67C23A; }
.stat-card--score    { border-top: 3px solid #E6A23C; }
.stat-card--total    { border-top: 3px solid #909399; }

/* 图表卡片 */
.chart-card {
  margin-bottom: 20px;
  border-radius: 8px;
}
.charts-row {
  margin-bottom: 0;
}
</style>
