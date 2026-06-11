// 记账首页
Page({
  data: {
    currentMonth: '',
    transactions: [],
    monthlyIncome: 0,
    monthlyExpense: 0,
  },

  onLoad() {
    const now = new Date()
    const month = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
    this.setData({ currentMonth: month })
    this.fetchTransactions()
  },

  onShow() {
    this.fetchTransactions()
  },

  fetchTransactions() {
    // TODO: 调用后端 API 获取账单列表
  },

  onAddTap() {
    // TODO: 打开添加账单弹窗
  },
})
