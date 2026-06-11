// 记账首页
const api = require('../../utils/api')

Page({
  data: {
    // 月份
    currentMonth: '',     // YYYY-MM
    currentMonthLabel: '', // 2026年6月

    // 汇总
    monthlyIncome: 0,
    monthlyExpense: 0,

    // 账单列表（按日期分组）
    groupedTransactions: [], // [{date, dateLabel, items: [...], dayIncome, dayExpense}]

    // 添加弹窗
    showAddDialog: false,
    addType: 'expense',  // 'expense' | 'income'
    addAmount: '',
    addCategory: '',
    addDate: '',
    addNote: '',

    // 分类列表
    expenseCategories: ['餐饮', '交通', '购物', '住房', '娱乐', '医疗', '教育', '其他'],
    incomeCategories: ['工资', '奖金', '理财', '兼职', '其他'],

    // 加载
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
    this.loadTransactions()
  },

  /** 加载账单 */
  async loadTransactions() {
    if (!this.data.currentMonth) return

    this.setData({ loading: true })
    try {
      const result = await api.get('/transaction/list', { month: this.data.currentMonth })
      const grouped = this.groupByDate(result.items)

      this.setData({
        monthlyIncome: result.total_income,
        monthlyExpense: result.total_expense,
        groupedTransactions: grouped,
        loading: false,
      })
    } catch (err) {
      this.setData({ loading: false })
      if (!err.message.includes('还没有加入')) {
        wx.showToast({ title: err.message, icon: 'none' })
      }
    }
  },

  /** 按日期分组 */
  groupByDate(items) {
    const map = {}
    items.forEach(item => {
      if (!map[item.date]) {
        map[item.date] = { date: item.date, dateLabel: '', items: [], dayIncome: 0, dayExpense: 0 }
      }
      map[item.date].items.push(item)
      if (item.type === 'income') {
        map[item.date].dayIncome += item.amount
      } else {
        map[item.date].dayExpense += item.amount
      }
    })

    return Object.values(map)
      .sort((a, b) => b.date.localeCompare(a.date))
      .map(g => {
        const d = new Date(g.date)
        g.dateLabel = `${d.getMonth() + 1}月${d.getDate()}日 周${['日','一','二','三','四','五','六'][d.getDay()]}`
        g.dayIncome = Math.round(g.dayIncome * 100) / 100
        g.dayExpense = Math.round(g.dayExpense * 100) / 100
        return g
      })
  },

  // ---------- 月份切换 ----------

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
    this.loadTransactions()
  },

  // ---------- 添加账单 ----------

  onOpenAdd() {
    const now = new Date()
    const date = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
    this.setData({
      showAddDialog: true,
      addType: 'expense',
      addAmount: '',
      addCategory: '',
      addDate: date,
      addNote: '',
    })
  },

  onCloseAdd() {
    this.setData({ showAddDialog: false })
  },

  onTypeTap(e) {
    const type = e.currentTarget.dataset.type
    this.setData({ addType: type, addCategory: '' })
  },

  onAmountInput(e) {
    this.setData({ addAmount: e.detail.value })
  },

  onCategoryTap(e) {
    this.setData({ addCategory: e.currentTarget.dataset.cat })
  },

  onDateChange(e) {
    this.setData({ addDate: e.detail.value })
  },

  onNoteInput(e) {
    this.setData({ addNote: e.detail.value })
  },

  /** 确认添加 */
  async onConfirmAdd() {
    const { addAmount, addCategory, addDate, addType } = this.data
    const amount = parseFloat(addAmount)

    if (!addAmount || isNaN(amount) || amount <= 0) {
      wx.showToast({ title: '请输入有效金额', icon: 'none' })
      return
    }
    if (!addCategory) {
      wx.showToast({ title: '请选择分类', icon: 'none' })
      return
    }

    try {
      wx.showLoading({ title: '保存中...' })
      await api.post('/transaction/add', {
        amount,
        category: addCategory,
        type: addType,
        date: addDate,
        note: this.data.addNote,
      })
      wx.hideLoading()

      this.setData({ showAddDialog: false })
      wx.showToast({ title: '已记录', icon: 'success' })
      this.loadTransactions()
    } catch (err) {
      wx.hideLoading()
      wx.showToast({ title: err.message, icon: 'none' })
    }
  },

  // ---------- 删除账单 ----------

  onDeleteItem(e) {
    const { id } = e.currentTarget.dataset
    wx.showModal({
      title: '确认删除',
      content: '删除后无法恢复',
      confirmColor: '#F44336',
      success: async (res) => {
        if (!res.confirm) return
        try {
          await api.del(`/transaction/${id}`)
          wx.showToast({ title: '已删除', icon: 'success' })
          this.loadTransactions()
        } catch (err) {
          wx.showToast({ title: err.message, icon: 'none' })
        }
      },
    })
  },

  /** 阻止弹窗冒泡 */
  noop() {},
})
