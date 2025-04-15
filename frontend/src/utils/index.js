import TaskStatusIcon from '@/components/Icons/TaskStatusIcon.vue'
import TaskPriorityIcon from '@/components/Icons/TaskPriorityIcon.vue'
import { useDateFormat, useTimeAgo } from '@vueuse/core'
import { usersStore } from '@/stores/users'
import { gemoji } from 'gemoji'
import { toast } from 'frappe-ui'
import { h } from 'vue'
import slugify from 'slugify'
import dayjs from 'dayjs'

slugify.extend({
  $: '',
  '%': '',
  '&': '',
  '>': '',
  '<': '',
  '|': '',
})

export function customSlugify(val) {
  return slugify(val, {
    lower: true,
    remove: /[^\w\s]/g,
    strict: true,
    locale: 'vi',
  })
}

export function validErrApi(err, router) {
  if (err) {
    switch (err.exc_type) {
      case 'PermissionError':
        router.push('/permission-denied')
        return
      case 'AuthenticationError':
        window.location.href = '/cms/login'
        return
      default:
        return
    }
  }
}

export function createToast(options) {
  toast({
    position: 'bottom-right',
    ...options,
  })
}

export function formatTime(seconds) {
  const days = Math.floor(seconds / (3600 * 24))
  const hours = Math.floor((seconds % (3600 * 24)) / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const remainingSeconds = Math.floor(seconds % 60)

  let formattedTime = ''

  if (days > 0) {
    formattedTime += `${days}d `
  }

  if (hours > 0 || days > 0) {
    formattedTime += `${hours}h `
  }

  if (minutes > 0 || hours > 0 || days > 0) {
    formattedTime += `${minutes}m `
  }

  formattedTime += `${remainingSeconds}s`

  return formattedTime.trim()
}

function prettyDate(date, mini) {
  if (!date) return ''

  // Thời gian ban đầu
  const d = dayjs(date)
  // Thời gian hiện tại
  const now = dayjs()

  // Tính khoảng cách thời gian ra giây
  const diff = now.diff(d, 'second')
  let day_diff = Math.floor(diff / 86400)
  if (isNaN(day_diff) || day_diff < 0) return ''

  if (mini) {
    // Return short format of time difference
    if (day_diff == 0) {
      if (diff < 60) {
        return __('now')
      } else if (diff < 3600) {
        return __('{0} m', [Math.floor(diff / 60)])
      } else if (diff < 86400) {
        return __('{0} h', [Math.floor(diff / 3600)])
      }
    } else {
      if (day_diff < 7) {
        return __('{0} d', [day_diff])
      } else if (day_diff < 31) {
        return __('{0} w', [Math.floor(day_diff / 7)])
      } else if (day_diff < 365) {
        return __('{0} M', [Math.floor(day_diff / 30)])
      } else {
        return __('{0} y', [Math.floor(day_diff / 365)])
      }
    }
  } else {
    // Return long format of time difference
    if (day_diff == 0) {
      if (diff < 60) {
        return __('just now')
      } else if (diff < 120) {
        return __('1 minute ago')
      } else if (diff < 3600) {
        return __('{0} minutes ago', [Math.floor(diff / 60)])
      } else if (diff < 7200) {
        return __('1 hour ago')
      } else if (diff < 86400) {
        return __('{0} hours ago', [Math.floor(diff / 3600)])
      }
    } else {
      if (day_diff == 1) {
        return __('yesterday')
      } else if (day_diff < 7) {
        return __('{0} days ago', [day_diff])
      } else if (day_diff < 14) {
        return __('1 week ago')
      } else if (day_diff < 31) {
        return __('{0} weeks ago', [Math.floor(day_diff / 7)])
      } else if (day_diff < 62) {
        return __('1 month ago')
      } else if (day_diff < 365) {
        return __('{0} months ago', [Math.floor(day_diff / 30)])
      } else if (day_diff < 730) {
        return __('1 year ago')
      } else {
        return __('{0} years ago', [Math.floor(day_diff / 365)])
      }
    }
  }
}

export function dateFormat(date, format) {
  const _format = format || 'DD-MM-YYYY HH:mm:ss'
  return useDateFormat(date, _format).value
}

export function timeAgo(date) {
  return prettyDate(date)
  // return useTimeAgo(date).value
}

export const dateTooltipFormat = 'ddd, MMM D, YYYY h:mm A'

export function taskStatusOptions(action, data) {
  return ['Backlog', 'Todo', 'In Progress', 'Done', 'Canceled'].map(
    (status) => {
      return {
        icon: () => h(TaskStatusIcon, { status }),
        label: status,
        onClick: () => action && action(status, data),
      }
    },
  )
}

export function taskPriorityOptions(action, data) {
  return ['Low', 'Medium', 'High'].map((priority) => {
    return {
      label: priority,
      icon: () => h(TaskPriorityIcon, { priority }),
      onClick: () => action && action(priority, data),
    }
  })
}

export function openWebsite(url) {
  window.open(url, '_blank')
}

export function htmlToText(html) {
  const div = document.createElement('div')
  div.innerHTML = html
  return div.textContent || div.innerText || ''
}

export function secondsToDuration(seconds) {
  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const _seconds = Math.floor((seconds % 3600) % 60)

  if (hours == 0 && minutes == 0) {
    return `${_seconds}s`
  } else if (hours == 0) {
    return `${minutes}m ${_seconds}s`
  }
  return `${hours}h ${minutes}m ${_seconds}s`
}

export function formatNumberIntoCurrency(value) {
  if (value) {
    return value.toLocaleString('en-IN', {
      maximumFractionDigits: 2,
      style: 'currency',
      currency: 'INR',
    })
  }
  return ''
}

export function formatNumber(val, decimal = 1) {
  let rs = 0
  if (val) {
    if (Number.isInteger(val)) {
      rs = new Intl.NumberFormat('en-US').format(val)
    } else {
      rs = new Intl.NumberFormat('en-US', {
        minimumFractionDigits: decimal,
        maximumFractionDigits: decimal,
      }).format(val)
    }
  }

  return rs
}

export function startCase(str) {
  return str.charAt(0).toUpperCase() + str.slice(1)
}

export function validateEmail(email) {
  let regExp =
    /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
  return regExp.test(email)
}

export function setupAssignees(data) {
  let { getUser } = usersStore()
  let assignees = data._assign || []
  data._assignedTo = assignees.map((user) => ({
    name: user,
    image: getUser(user).user_image,
    label: getUser(user).full_name,
  }))
}

export function setupCustomActions(data, obj) {
  if (!data._form_script) return []
  let script = new Function(data._form_script + '\nreturn setupForm')()
  let formScript = script(obj)
  data._customActions = formScript?.actions || []
}

export function setupListActions(data, obj = {}) {
  if (!data.list_script) return []
  let script = new Function(data.list_script + '\nreturn setupList')()
  let listScript = script(obj)
  data.listActions = listScript?.actions || []
  data.bulkActions = listScript?.bulk_actions || []
}

export function errorMessage(title, message) {
  createToast({
    title: title || 'Error',
    text: message,
    icon: 'x',
    iconClasses: 'text-red-600',
  })
}

export function warningMessage(title, message) {
  createToast({
    title: title || 'Warning',
    text: message,
    icon: 'alert-circle',
    iconClasses: 'text-orange-600',
  })
}

export function getTypeField(name) {
  switch (name) {
    case 'Select':
      return 'select'
    case 'Data':
      return 'text'
    case 'Link':
      return 'link'
    case 'Text':
      return 'text'
    case 'Attach':
      return 'upload_image'
    default:
      return name
  }
}

export function copyToClipboard(text) {
  if (navigator.clipboard && window.isSecureContext) {
    navigator.clipboard.writeText(text).then(show_success_alert)
  } else {
    let input = document.createElement('textarea')
    document.body.appendChild(input)
    input.value = text
    input.select()
    document.execCommand('copy')
    show_success_alert()
    document.body.removeChild(input)
  }
  function show_success_alert() {
    createToast({
      title: 'Copied to clipboard',
      text: text,
      icon: 'check',
      iconClasses: 'text-green-600',
    })
  }
}

export function isEmoji(str) {
  const emojiList = gemoji.map((emoji) => emoji.emoji)
  return emojiList.includes(str)
}

export async function uploadFile(
  doctype,
  docname,
  fieldname,
  file_url_old,
  upload_file_image,
) {
  let file_url = ''
  let headers = { Accept: 'application/json' }
  if (window.csrf_token && window.csrf_token !== '{{ csrf_token }}') {
    headers['X-Frappe-CSRF-Token'] = window.csrf_token
  }

  let imgForm = new FormData()
  imgForm.append('file', upload_file_image, upload_file_image.name)
  imgForm.append('is_private', 0)
  imgForm.append('doctype', doctype)
  imgForm.append('fieldname', fieldname)
  imgForm.append('docname', docname)
  imgForm.append('file_url_old', file_url_old)

  await fetch('/api/method/go1_cms.api.handler_file.upload_file', {
    headers: headers,
    method: 'POST',
    body: imgForm,
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.message) {
        file_url = data.message.file_url
      }
    })
    .catch((err) => {
      if (err.messages && err.messages.length) {
        msgError.value = err.messages.join(', ')
        errorMessage(__('An error has occurred'), err.messages.join(', '))
      } else {
        errorMessage(__('An error has occurred'), err)
      }
    })

  return file_url
}

export async function handleUploadFieldImage(data, _page, doctype, docname) {
  // upload image
  if (_page.value?.fields_cp) {
    for (const [idx_cp, field] of _page.value.fields_cp.entries()) {
      for (const [idx_f, f] of field.fields.entries()) {
        if (f.group_name) {
          for (const [idx, f_st] of f.fields.entries()) {
            if (
              ['Attach', 'upload_image'].includes(f_st.field_type) &&
              f_st.upload_file_image
            ) {
              // upload file
              let file_url = await uploadFile(
                doctype,
                docname,
                f_st.field_key,
                f_st.content,
                f_st.upload_file_image,
              )
              data['fields_cp'][idx_cp]['fields'][idx_f]['fields'][idx][
                'content'
              ] = file_url
            }
          }
        } else {
          if (
            ['Attach', 'upload_image'].includes(f.field_type) &&
            f.upload_file_image
          ) {
            // upload file
            let file_url = await uploadFile(
              doctype,
              docname,
              f.field_key,
              f.content,
              f.upload_file_image,
            )
            data['fields_cp'][idx_cp]['fields'][idx_f]['content'] = file_url
          }
        }
      }
    }
  }
  if (_page.value?.fields_st_cp) {
    for (const [idx_cp, field] of _page.value.fields_st_cp.entries()) {
      for (const [idx_f, f] of field.fields.entries()) {
        if (f.group_name) {
          for (const [idx, f_st] of f.fields.entries()) {
            if (f_st.field_type == 'Attach' && f_st.upload_file_image) {
              // upload file
              let file_url = await uploadFile(
                doctype,
                docname,
                f_st.field_key,
                f_st.content,
                f_st.upload_file_image,
              )
              data['fields_st_cp'][idx_cp]['fields'][idx_f]['fields'][idx][
                'content'
              ] = file_url
            } else if (f_st.field_type == 'List') {
              for (const [idx_f_ps, f_ps] of f_st.content.entries()) {
                for (const [idx_f_js, f_js] of f_st.fields_json.entries()) {
                  if (
                    f_js.field_type == 'Attach' &&
                    f_ps['upload_file_image_' + f_js.field_key]
                  ) {
                    // upload file
                    let file_url = await uploadFile(
                      doctype,
                      docname,
                      f_js.field_key,
                      f_ps[f_js.field_key],
                      f_ps['upload_file_image_' + f_js.field_key],
                    )
                    f_ps[f_js.field_key] = file_url
                  }
                  delete f_ps['upload_file_image_' + f_js.field_key]
                  data['fields_st_cp'][idx_cp]['fields'][idx_f]['fields'][idx][
                    'content'
                  ][idx_f_ps] = { ...f_ps }
                }
              }
            }
          }
        } else {
          if (f.field_type == 'Attach' && f.upload_file_image) {
            // upload file
            let file_url = await uploadFile(
              doctype,
              docname,
              f.field_key,
              f.content,
              f.upload_file_image,
            )
            data['fields_st_cp'][idx_cp]['fields'][idx_f]['content'] = file_url
          } else if (f.field_type == 'List') {
            for (const [idx_f_ps, f_ps] of f.content.entries()) {
              for (const [idx_f_js, f_js] of f.fields_json.entries()) {
                if (
                  f_js.field_type == 'Attach' &&
                  f_ps['upload_file_image_' + f_js.field_key]
                ) {
                  // upload file
                  let file_url = await uploadFile(
                    doctype,
                    docname,
                    f_js.field_key,
                    f_ps[f_js.field_key],
                    f_ps['upload_file_image_' + f_js.field_key],
                  )

                  f_ps[f_js.field_key] = file_url
                }
                delete f_ps['upload_file_image_' + f_js.field_key]
                data['fields_st_cp'][idx_cp]['fields'][idx_f]['content'][
                  idx_f_ps
                ] = { ...f_ps }
              }
            }
          }
        }
      }
    }
  }
}

export const toBase64 = (file) =>
  new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.readAsDataURL(file)
    reader.onload = () => resolve(reader.result)
    reader.onerror = reject
  })

export function scrollToTop(refToTop) {
  refToTop.value.scrollTo(0, 0)
}

export function areDeeplyEqual(obj1, obj2) {
  if (obj1 === obj2) return true

  if (Array.isArray(obj1) && Array.isArray(obj2)) {
    if (obj1.length !== obj2.length) return false

    return obj1.every((elem, index) => {
      return areDeeplyEqual(elem, obj2[index])
    })
  }

  if (
    typeof obj1 === 'object' &&
    typeof obj2 === 'object' &&
    obj1 !== null &&
    obj2 !== null
  ) {
    if (Array.isArray(obj1) || Array.isArray(obj2)) return false

    const keys1 = Object.keys(obj1)
    const keys2 = Object.keys(obj2)

    if (
      keys1.length !== keys2.length ||
      !keys1.every((key) => keys2.includes(key))
    )
      return false

    for (let key in obj1) {
      let isEqual = areDeeplyEqual(obj1[key], obj2[key])
      if (!isEqual) {
        return false
      }
    }

    return true
  }

  return false
}

export function getCurrentDateInVietnam() {
  const today = new Date()
  // Thêm 7 giờ vào thời gian UTC để có thời gian Việt Nam
  today.setUTCHours(today.getUTCHours() + 7)

  const year = today.getUTCFullYear()
  const month = String(today.getUTCMonth() + 1).padStart(2, '0') // Tháng bắt đầu từ 0 nên cần +1
  const day = String(today.getUTCDate()).padStart(2, '0')

  return `${year}-${month}-${day}`
}

export function getDateMinusDays(dateString, days, operator = '-') {
  const today = new Date(dateString)
  if (operator == '-') {
    today.setDate(today.getDate() - days)
  } else {
    today.setDate(today.getDate() + days)
  }

  const year = today.getUTCFullYear()
  const month = String(today.getUTCMonth() + 1).padStart(2, '0') // Tháng bắt đầu từ 0 nên cần +1
  const day = String(today.getUTCDate()).padStart(2, '0')

  return `${year}-${month}-${day}`
}
