<template>
  <div id="app">
    <el-container>
      <!-- 侧边导航 -->
      <el-aside width="220px">
        <div class="logo">🎯 HR 智能招聘</div>
        <el-menu
          :default-active="activeMenu"
          router
          background-color="#304156"
          text-color="#bfcbd9"
          active-text-color="#409EFF"
        >
          <!-- 新增：Dashboard 数据概览入口，放置在最前面 -->
          <el-menu-item index="/dashboard">
            <el-icon><DataAnalysis /></el-icon>
            <span>数据概览</span>
          </el-menu-item>
          <el-menu-item index="/match">
            <el-icon><DocumentChecked /></el-icon>
            <span>候选人匹配筛查</span>
          </el-menu-item>
          <el-menu-item index="/interview">
            <el-icon><ChatLineSquare /></el-icon>
            <span>面试一致性评估</span>
          </el-menu-item>
          <el-menu-item index="/history">
            <el-icon><Clock /></el-icon>
            <span>历史记录</span>
          </el-menu-item>
        </el-menu>
      </el-aside>

      <!-- 主内容区 -->
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const activeMenu = computed(() => route.path)
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', Arial, sans-serif;
}

.el-aside {
  background-color: #304156;
  min-height: 100vh;
}

.logo {
  color: #fff;
  font-size: 18px;
  font-weight: bold;
  padding: 20px 16px;
  text-align: center;
  border-bottom: 1px solid #4a5064;
}

.el-main {
  background-color: #f0f2f5;
  min-height: 100vh;
  padding: 24px;
}
</style>
