import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'
import { userResource } from './user'
import { ref, computed } from 'vue'

export const sessionStore = defineStore('cms-session', () => {
  function sessionUser() {
    let cookies = new URLSearchParams(document.cookie.split('; ').join('&'))
    let _sessionUser = cookies.get('user_id')
    if (_sessionUser === 'Guest') {
      _sessionUser = null
    }
    return _sessionUser
  }

  let user = ref(sessionUser())
  const isLoggedIn = computed(() => !!user.value)

  const login = createResource({
    url: 'login',
    onError() {
      throw new Error('Invalid email or password')
    },
    onSuccess() {
      userResource.reload()
      user.value = sessionUser()
      login.reset()
      window.location.href = '/cms'
    },
  })

  const logout = createResource({
    url: 'logout',
    onSuccess() {
      userResource.reset()
      user.value = null
      window.location.href = '/cms/login'
    },
  })

  return {
    user,
    isLoggedIn,
    login,
    logout,
  }
})
