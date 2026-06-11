// 统计看板
const api = require('../../utils/api')

Page({
  data: {
    currentMonth: '',
    currentMonthLabel: '',
    totalIncome: 0,
    totalExpense: 0,
    balance: 0,
    expenseByCategory: [],
    incomeByCategory: [],
    loading: false,
  },

  onLoad() {
    const now = new Date()
    const month = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
    this.setData({
      currentMonth: month,
      currentMonthLabel: `${now.getFullYear()}年${now.getMonth() + 1}月`,
    })
  },

  onShow() {
    this.loadStats()
  },

  async loadStats() {
    if (!this.data.currentMonth) return

    this.setData({ loading: true })
    try {
      const result = await api.get('/transaction/stats', { month: this.data.currentMonth })
      this.setData({
        totalIncome: result.total_income,
        totalExpense: result.total_expense,
        balance: result.balance,
        expenseByCategory: result.expense_by_category,
        incomeByCategory: result.income_by_category,
        loading: false,
      })
    } catch (err) {
      this.setData({ loading: false })
      if (!err.message.includes('还没有加入')) {
        wx.showToast({ title: err.message, icon: 'none' })
      }
    }
  },

  onPrevMonth() {
    this.shiftMonth(-1)
  },

  onNextMonth() {
    this.shiftMonth(1)
  },

  shiftMonth(delta) {
    const [y, m] = this.data.currentMonth.split('-').map(Number)
    const d = new Date(y, m - 1 + delta, 1)
    const month = `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}`
    this.setData({
      currentMonth: month,
      currentMonthLabel: `${d.getFullYear()}年${d.getMonth() + 1}月`,
    })
    this.loadStats()
  },
})
