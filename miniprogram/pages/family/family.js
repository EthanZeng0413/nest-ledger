// 家庭管理
const api = require('../../utils/api')

Page({
  data: {
    // 家庭信息
    familyInfo: null, // { family_id, name, invite_code, my_role }
    members: [],
    isCreator: false,
    inviteCode: '',

    // 弹窗状态
    showCreateDialog: false,
    showJoinDialog: false,
    createName: '',
    joinCode: '',

    // 加载状态
    loading: true,
    errorMsg: '',
  },

  onShow() {
    this.loadFamilyInfo()
  },

  /** 加载家庭信息 */
  async loadFamilyInfo() {
    this.setData({ loading: true, errorMsg: '' })
    try {
      const info = await api.get('/family/info')
      this.setData({
        familyInfo: info,
        members: info.members,
        isCreator: info.my_role === 'creator',
        inviteCode: info.invite_code,
        loading: false,
      })
    } catch (err) {
      // 404 表示未加入家庭
      if (err.message.includes('还没有加入') || err.message.includes('不存在')) {
        this.setData({ familyInfo: null, members: [], loading: false })
      } else {
        this.setData({ loading: false, errorMsg: err.message })
      }
    }
  },

  // ---------- 创建家庭 ----------

  /** 打开创建弹窗 */
  onOpenCreate() {
    this.setData({ showCreateDialog: true, createName: '' })
  },

  /** 关闭创建弹窗 */
  onCloseCreate() {
    this.setData({ showCreateDialog: false })
  },

  /** 输入家庭名称 */
  onNameInput(e) {
    this.setData({ createName: e.detail.value })
  },

  /** 确认创建 */
  async onConfirmCreate() {
    const name = this.data.createName.trim()
    if (!name) {
      wx.showToast({ title: '请输入家庭名称', icon: 'none' })
      return
    }
    if (name.length < 2) {
      wx.showToast({ title: '名称至少2个字', icon: 'none' })
      return
    }

    try {
      wx.showLoading({ title: '创建中...' })
      const result = await api.post('/family/create', { name })
      wx.hideLoading()

      this.setData({ showCreateDialog: false })
      wx.showModal({
        title: '创建成功',
        content: `邀请码：${result.invite_code}\n\n将此邀请码分享给家人，他们输入邀请码即可加入`,
        showCancel: false,
        success: () => this.loadFamilyInfo(),
      })
    } catch (err) {
      wx.hideLoading()
      wx.showToast({ title: err.message, icon: 'none' })
    }
  },

  // ---------- 加入家庭 ----------

  /** 打开加入弹窗 */
  onOpenJoin() {
    this.setData({ showJoinDialog: true, joinCode: '' })
  },

  /** 关闭加入弹窗 */
  onCloseJoin() {
    this.setData({ showJoinDialog: false })
  },

  /** 输入邀请码 */
  onCodeInput(e) {
    this.setData({ joinCode: e.detail.value.toUpperCase() })
  },

  /** 确认加入 */
  async onConfirmJoin() {
    const code = this.data.joinCode.trim()
    if (code.length !== 6) {
      wx.showToast({ title: '请输入6位邀请码', icon: 'none' })
      return
    }

    try {
      wx.showLoading({ title: '加入中...' })
      const result = await api.post('/family/join', { invite_code: code })
      wx.hideLoading()

      this.setData({ showJoinDialog: false })
      wx.showToast({ title: result.message, icon: 'success' })
      setTimeout(() => this.loadFamilyInfo(), 1000)
    } catch (err) {
      wx.hideLoading()
      wx.showToast({ title: err.message, icon: 'none' })
    }
  },

  // ---------- 退出家庭 ----------

  /** 退出家庭 */
  onLeaveFamily() {
    wx.showModal({
      title: '确认退出',
      content: this.data.isCreator
        ? '你是家庭创建者，退出将解散家庭，所有数据将被删除。确认退出？'
        : '退出后你将无法查看家庭账单和日历。确认退出？',
      confirmColor: '#F44336',
      success: async (res) => {
        if (!res.confirm) return

        try {
          wx.showLoading({ title: '退出中...' })
          await api.post('/family/leave')
          wx.hideLoading()

          wx.showToast({ title: '已退出', icon: 'success' })
          setTimeout(() => this.loadFamilyInfo(), 1000)
        } catch (err) {
          wx.hideLoading()
          wx.showToast({ title: err.message, icon: 'none' })
        }
      },
    })
  },

  // ---------- 复制邀请码 ----------

  /** 复制邀请码到剪贴板 */
  onCopyInviteCode() {
    wx.setClipboardData({
      data: this.data.inviteCode,
      success: () => {
        wx.showToast({ title: '邀请码已复制', icon: 'success' })
      },
    })
  },
})
