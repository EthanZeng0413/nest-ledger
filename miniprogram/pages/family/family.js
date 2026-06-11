// 家庭设置
Page({
  data: {
    familyInfo: null,
    members: [],
    isCreator: false,
    inviteCode: '',
  },

  onLoad() {
    this.fetchFamilyInfo()
  },

  onShow() {
    this.fetchFamilyInfo()
  },

  fetchFamilyInfo() {
    // TODO: 调用后端 API 获取家庭信息
  },

  onCreateFamily() {
    // TODO: 创建家庭
  },

  onJoinFamily() {
    // TODO: 加入家庭
  },

  onLeaveFamily() {
    // TODO: 退出家庭
  },
})
