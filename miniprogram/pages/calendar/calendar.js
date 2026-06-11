// 共享日历
const api = require('../../utils/api')

Page({
  data: {
    // 当前显示的年月
    currentYear: 0,
    currentMonth: 0,
    currentMonthLabel: '',

    // 日历网格
    weekDays: ['日', '一', '二', '三', '四', '五', '六'],
    days: [],  // [{day, dateStr, isCurrentMonth, hasEvent, events: [...]}]

    // 事件
    allEvents: [],  // 当月所有事件
    selectedDate: '',
    selectedDateLabel: '',
    selectedDateEvents: [],

    // 添加/编辑弹窗
    showDialog: false,
    editMode: false,       // 'create' | 'edit'
    editEventId: '',
    eventTitle: '',
    eventStartTime: '',
    eventRepeatType: 'none',
    eventRepeatDay: 0,
    eventNote: '',

    // 加载
    loading: false,
  },

  onLoad() {
    const now = new Date()
    this.setData({
      currentYear: now.getFullYear(),
      currentMonth: now.getMonth() + 1,
      currentMonthLabel: `${now.getFullYear()}年${now.getMonth() + 1}月`,
    })
    this.renderCalendar()
  },

  onShow() {
    this.loadEvents()
  },

  /** 加载当月事件 */
  async loadEvents() {
    const month = `${this.data.currentYear}-${String(this.data.currentMonth).padStart(2, '0')}`
    this.setData({ loading: true })
    try {
      const result = await api.get('/event/list', { month })
      this.setData({ allEvents: result.events, loading: false })
      this.renderCalendar()
    } catch (err) {
      this.setData({ loading: false })
      if (!err.message.includes('还没有加入')) {
        console.error('加载日历事件失败:', err.message)
      }
    }
  },

  /** 渲染日历网格 */
  renderCalendar() {
    const { currentYear, currentMonth, allEvents } = this.data
    const daysInMonth = new Date(currentYear, currentMonth, 0).getDate()
    const firstDayOfWeek = new Date(currentYear, currentMonth - 1, 1).getDay() // 0=Sun
    const prevMonthDays = new Date(currentYear, currentMonth - 1, 0).getDate()

    const days = []

    // 上月填充
    for (let i = firstDayOfWeek - 1; i >= 0; i--) {
      const day = prevMonthDays - i
      const dateStr = this.buildDateStr(currentYear, currentMonth - 1, day)
      days.push({
        day,
        dateStr,
        isCurrentMonth: false,
        hasEvent: false,
        events: [],
      })
    }

    // 当月
    for (let d = 1; d <= daysInMonth; d++) {
      const dateStr = this.buildDateStr(currentYear, currentMonth, d)
      const dayEvents = allEvents.filter(e => {
        if (e.repeat_type === 'none') {
          return e.start_time.startsWith(dateStr)
        }
        // 简单重复事件匹配
        return this.matchRepeatEvent(e, dateStr)
      })

      days.push({
        day: d,
        dateStr,
        isCurrentMonth: true,
        isToday: this.isToday(dateStr),
        hasEvent: dayEvents.length > 0,
        events: dayEvents,
      })
    }

    // 下月填充
    const remaining = 42 - days.length // 6行 × 7列
    for (let d = 1; d <= remaining; d++) {
      const dateStr = this.buildDateStr(currentYear, currentMonth + 1, d)
      days.push({
        day: d,
        dateStr,
        isCurrentMonth: false,
        hasEvent: false,
        events: [],
      })
    }

    this.setData({ days })
  },

  buildDateStr(year, month, day) {
    // 处理跨月/跨年
    const d = new Date(year, month - 1, day)
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  },

  isToday(dateStr) {
    const now = new Date()
    const today = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}-${String(now.getDate()).padStart(2, '0')}`
    return dateStr === today
  },

  /** 匹配重复事件 */
  matchRepeatEvent(event, dateStr) {
    const eventDate = new Date(event.start_time.slice(0, 10))
    const checkDate = new Date(dateStr)

    if (checkDate < eventDate) return false

    switch (event.repeat_type) {
      case 'daily':
        return true
      case 'weekly':
        return checkDate.getDay() + 1 === event.repeat_day // 1=Mon, 7=Sun... hmm
      case 'monthly':
        return checkDate.getDate() === event.repeat_day
      default:
        return false
    }
  },

  // ---------- 月份切换 ----------

  onPrevMonth() {
    this.shiftMonth(-1)
  },

  onNextMonth() {
    this.shiftMonth(1)
  },

  shiftMonth(delta) {
    let { currentYear, currentMonth } = this.data
    currentMonth += delta
    if (currentMonth > 12) { currentMonth = 1; currentYear++ }
    if (currentMonth < 1) { currentMonth = 12; currentYear-- }
    this.setData({
      currentYear,
      currentMonth,
      currentMonthLabel: `${currentYear}年${currentMonth}月`,
    })
    this.renderCalendar()
    this.loadEvents()
  },

  // ---------- 选择日期 ----------

  onDayTap(e) {
    const { dateStr } = e.currentTarget.dataset

    if (dateStr === this.data.selectedDate) {
      // 取消选择
      this.setData({ selectedDate: '', selectedDateLabel: '', selectedDateEvents: [] })
      return
    }

    const d = new Date(dateStr)
    const label = `${d.getMonth() + 1}月${d.getDate()}日 周${['日','一','二','三','四','五','六'][d.getDay()]}`

    const dayEvents = this.data.allEvents.filter(e => {
      if (e.repeat_type === 'none') return e.start_time.startsWith(dateStr)
      return this.matchRepeatEvent(e, dateStr)
    })

    this.setData({
      selectedDate: dateStr,
      selectedDateLabel: label,
      selectedDateEvents: dayEvents,
    })
  },

  // ---------- 添加事件 ----------

  onOpenAdd() {
    if (!this.data.selectedDate) {
      wx.showToast({ title: '请先点击日期', icon: 'none' })
      return
    }
    this.setData({
      showDialog: true,
      editMode: false,
      editEventId: '',
      eventTitle: '',
      eventStartTime: `${this.data.selectedDate} 09:00`,
      eventRepeatType: 'none',
      eventRepeatDay: 0,
      eventNote: '',
    })
  },

  onCloseDialog() {
    this.setData({ showDialog: false })
  },

  onTitleInput(e) {
    this.setData({ eventTitle: e.detail.value })
  },

  onTimeChange(e) {
    this.setData({ eventStartTime: e.detail.value })
  },

  onRepeatChange(e) {
    this.setData({ eventRepeatType: e.detail.value })
  },

  onNoteInput(e) {
    this.setData({ eventNote: e.detail.value })
  },

  /** 确认创建 */
  async onConfirmCreate() {
    const title = this.data.eventTitle.trim()
    if (!title) {
      wx.showToast({ title: '请输入事件标题', icon: 'none' })
      return
    }

    // 将 datetime-local 格式转为 ISO
    const startTime = this.data.eventStartTime.replace(' ', 'T') + ':00'

    const body = {
      title,
      start_time: startTime,
      repeat_type: this.data.eventRepeatType,
      repeat_day: this.data.eventRepeatDay,
      note: this.data.eventNote,
    }

    // 计算 repeat_day
    if (body.repeat_type === 'weekly') {
      body.repeat_day = new Date(this.data.selectedDate).getDay() + 1
    } else if (body.repeat_type === 'monthly') {
      body.repeat_day = new Date(this.data.selectedDate).getDate()
    }

    try {
      wx.showLoading({ title: '保存中...' })

      if (this.data.editMode) {
        await api.put(`/event/${this.data.editEventId}`, body)
      } else {
        await api.post('/event/create', body)
      }

      wx.hideLoading()
      this.setData({ showDialog: false })
      wx.showToast({ title: this.data.editMode ? '已更新' : '已创建', icon: 'success' })
      this.loadEvents()
    } catch (err) {
      wx.hideLoading()
      wx.showToast({ title: err.message, icon: 'none' })
    }
  },

  // ---------- 编辑 / 删除 ----------

  onEditEvent(e) {
    const event = e.currentTarget.dataset.event
    this.setData({
      showDialog: true,
      editMode: true,
      editEventId: event.id,
      eventTitle: event.title,
      eventStartTime: event.start_time.replace('T', ' ').slice(0, 16),
      eventRepeatType: event.repeat_type,
      eventNote: event.note,
    })
  },

  onDeleteEvent(e) {
    const { id } = e.currentTarget.dataset
    wx.showModal({
      title: '确认删除',
      content: '删除后无法恢复',
      confirmColor: '#F44336',
      success: async (res) => {
        if (!res.confirm) return
        try {
          await api.del(`/event/${id}`)
          wx.showToast({ title: '已删除', icon: 'success' })
          this.loadEvents()
        } catch (err) {
          wx.showToast({ title: err.message, icon: 'none' })
        }
      },
    })
  },

  noop() {},
})
