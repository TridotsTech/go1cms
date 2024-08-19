import { defineStore } from 'pinia'
import { getCurrentInstance, ref } from 'vue'

export const globalStore = defineStore('cms-global', () => {
  //
  const name_website_edit = ref()
  function changeNameWebsiteEdit(new_name) {
    name_website_edit.value = new_name
  }

  // loading
  const loadingValue = ref({
    active: false,
    text: 'Loading...',
  })

  function changeLoadingValue(active = false, text = 'Loading...') {
    loadingValue.value = {
      active,
      text,
    }
  }

  //
  const app = getCurrentInstance()
  const { $dialog, $socket } = app.appContext.config.globalProperties

  let twilioEnabled = ref(false)
  let callMethod = () => {}

  function setTwilioEnabled(value) {
    twilioEnabled.value = value
  }

  function setMakeCall(value) {
    callMethod = value
  }

  function makeCall(number) {
    callMethod(number)
  }

  return {
    name_website_edit,
    changeNameWebsiteEdit,
    loadingValue,
    changeLoadingValue,
    $dialog,
    $socket,
    twilioEnabled,
    makeCall,
    setTwilioEnabled,
    setMakeCall,
  }
})
