// 窝记 - 小程序入口
App({
  globalData: {
    // API 服务器地址，生产环境需修改
    apiBaseUrl: 'http://localhost:8000/api/v1',
    token: '',
    userInfo: null,
    familyInfo: null,
  },

  onLaunch() {
    // 检查登录状态
    const token = wx.getStorageSync('token')
    if (token) {
      this.globalData.token = token
    }
  },
})
