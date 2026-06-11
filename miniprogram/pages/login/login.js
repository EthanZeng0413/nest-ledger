// 登录页
const api = require('../../utils/api')
const app = getApp()

Page({
  data: {
    avatarUrl: '',
    nickname: '',
    isLoggingIn: false,
    errorMsg: '',
  },

  onLoad() {
    // 检查是否已登录
    const token = wx.getStorageSync('token')
    if (token) {
      app.globalData.token = token
      this.goHome()
    }
  },

  /** 选择头像 */
  onChooseAvatar(e) {
    this.setData({ avatarUrl: e.detail.avatarUrl })
  },

  /** 输入昵称 */
  onNicknameInput(e) {
    this.setData({ nickname: e.detail.value })
  },

  /** 微信登录 */
  async onLogin() {
    if (this.data.isLoggingIn) return

    this.setData({ isLoggingIn: true, errorMsg: '' })

    try {
      // 1. 获取微信登录 code
      const loginRes = await wx.login()
      if (!loginRes.code) {
        throw new Error('获取登录凭证失败')
      }

      // 2. 调用后端登录接口
      const result = await api.post('/auth/login', {
        code: loginRes.code,
        nickname: this.data.nickname,
        avatar_url: this.data.avatarUrl,
      })

      // 3. 存储 token
      wx.setStorageSync('token', result.token)
      app.globalData.token = result.token
      app.globalData.userInfo = {
        user_id: result.user_id,
        nickname: result.nickname,
      }

      wx.showToast({
        title: result.is_new ? '欢迎加入窝记' : '欢迎回来',
        icon: 'success',
      })

      // 4. 跳转首页
      setTimeout(() => this.goHome(), 1000)
    } catch (err) {
      this.setData({ errorMsg: err.message || '登录失败，请重试' })
    } finally {
      this.setData({ isLoggingIn: false })
    }
  },

  /** 跳转主页 */
  goHome() {
    wx.switchTab({ url: '/pages/index/index' })
  },
})
