// 共享日历
Page({
  data: {
    currentMonth: '',
    events: [],
    selectedDate: '',
    selectedDateEvents: [],
  },

  onLoad() {
    const now = new Date()
    const month = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`
    this.setData({ currentMonth: month })
    this.fetchEvents()
  },

  onShow() {
    this.fetchEvents()
  },

  fetchEvents() {
    // TODO: 调用后端 API 获取日历事件
  },

  onDateSelect(e) {
    // TODO: 处理日期选择
  },
})
