/** HTTP 请求封装 */
const app = getApp()

/**
 * 统一请求方法
 * @param {string} path - API 路径（不含 baseUrl）
 * @param {object} options - 请求选项
 */
function request(path, options = {}) {
  const { method = 'GET', data = {}, showLoading = false } = options

  if (showLoading) {
    wx.showLoading({ title: '加载中...' })
  }

  const token = wx.getStorageSync('token')
  const header = {
    'Content-Type': 'application/json',
  }
  if (token) {
    header['Authorization'] = `Bearer ${token}`
  }

  return new Promise((resolve, reject) => {
    wx.request({
      url: `${app.globalData.apiBaseUrl}${path}`,
      method,
      data,
      header,
      success(res) {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else if (res.statusCode === 401) {
          // Token 过期，触发重新登录
          wx.removeStorageSync('token')
          app.globalData.token = ''
          reject(new Error('登录已过期，请重新打开小程序'))
        } else {
          reject(new Error(res.data?.detail || '请求失败'))
        }
      },
      fail(err) {
        reject(new Error('网络连接失败'))
      },
      complete() {
        if (showLoading) {
          wx.hideLoading()
        }
      },
    })
  })
}

/** GET 请求 */
function get(path, data = {}) {
  const query = Object.keys(data)
    .filter(k => data[k] !== undefined && data[k] !== '')
    .map(k => `${k}=${encodeURIComponent(data[k])}`)
    .join('&')
  const url = query ? `${path}?${query}` : path
  return request(url, { method: 'GET' })
}

/** POST 请求 */
function post(path, data = {}) {
  return request(path, { method: 'POST', data })
}

/** PUT 请求 */
function put(path, data = {}) {
  return request(path, { method: 'PUT', data })
}

/** DELETE 请求 */
function del(path) {
  return request(path, { method: 'DELETE' })
}

module.exports = { get, post, put, del }
