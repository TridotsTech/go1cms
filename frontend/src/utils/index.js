import TaskStatusIcon from '@/components/Icons/TaskStatusIcon.vue'
import TaskPriorityIcon from '@/components/Icons/TaskPriorityIcon.vue'
import { useDateFormat, useTimeAgo } from '@vueuse/core'
import { usersStore } from '@/stores/users'
import { gemoji } from 'gemoji'
import { toast } from 'frappe-ui'
import { h } from 'vue'

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

export function dateFormat(date, format) {
  const _format = format || 'DD-MM-YYYY HH:mm:ss'
  return useDateFormat(date, _format).value
}

export function timeAgo(date) {
  return useTimeAgo(date).value
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
    case 'Small Text':
      return 'textarea'
    case 'Long Text':
      return 'textarea'
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
        errorMessage('Có lỗi xảy ra', err.messages.join(', '))
      } else {
        errorMessage('Có lỗi xảy ra', err)
      }
    })

  return file_url
}

export async function handleUploadFieldImage(data, _page, doctype, docname) {
  // upload image
  for (const [idx_cp, field] of _page.value.fields_cp.entries()) {
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
            data['fields_cp'][idx_cp]['fields'][idx_f]['fields'][idx][
              'content'
            ] = file_url
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
          data['fields_cp'][idx_cp]['fields'][idx_f]['content'] = file_url
        }
      }
    }
  }

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
