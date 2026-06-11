// 统计看板
Page({
  data: {
    currentMonth: '',
    totalIncome: 0,
    totalExpense: 0,
    balance: 0,
    categoryStats: [],  // [{category, amount, percent}]
  },

  onLoad() {
    const now = new Date()
    const month = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
    this.setData({ currentMonth: month })
    this.fetchStats()
  },

  onShow() {
    this.fetchStats()
  },

  fetchStats() {
    // TODO: 调用后端 API 获取统计数据
  },
})
