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
  function sessionUserSystem() {
    let cookies = new URLSearchParams(document.cookie.split('; ').join('&'))
    let _systemUser = cookies.get('system_user') === 'yes' ? true : false
    return _systemUser
  }

  let user = ref(sessionUser())
  const isLoggedIn = computed(() => !!user.value)
  const isSystemUser = computed(() => sessionUserSystem())

  const login = createResource({
    url: 'go1_cms.api.auth.login',
    onError() {
      throw new Error(__('Incorrect email or password.'))
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
    isSystemUser,
    login,
    logout,
  }
})
