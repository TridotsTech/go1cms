import './index.css'

import { createApp } from 'vue'
import router from './router'
import App from './App.vue'
import { createPinia } from 'pinia'
import CKEditor from '@ckeditor/ckeditor5-vue'

import {
  FrappeUI,
  Button,
  Input,
  TextInput,
  FormControl,
  ErrorMessage,
  Dialog,
  Alert,
  Badge,
  setConfig,
  frappeRequest,
  FeatherIcon,
  Tooltip,
} from 'frappe-ui'
import LoadingIndicator from '@/components/Icons/LoadingIndicator.vue'

import translationPlugin from './translation'
import { createDialog } from './utils/dialogs'
import { initSocket } from './socket'

import vue3PhotoPreview from 'vue3-photo-preview'
import 'vue3-photo-preview/dist/index.css'

let globalComponents = {
  Button,
  TextInput,
  Input,
  FormControl,
  ErrorMessage,
  Dialog,
  Alert,
  Badge,
  FeatherIcon,
  Tooltip,
  LoadingIndicator,
}

// create a pinia instance
let pinia = createPinia()

let app = createApp(App)

setConfig('resourceFetcher', frappeRequest)

// if (!import.meta.env.DEV) {
//   app.use(FrappeUI)
// }
app.use(CKEditor)
app.use(pinia)
app.use(router)
app.use(translationPlugin)
app.use(vue3PhotoPreview)
for (let key in globalComponents) {
  app.component(key, globalComponents[key])
}

app.config.globalProperties.$dialog = createDialog

let socket
if (import.meta.env.DEV) {
  frappeRequest({
    url: '/api/method/go1_cms.www.cms.get_context_for_dev',
  }).then((values) => {
    for (let key in values) {
      window[key] = values[key]
    }
    socket = initSocket()
    app.config.globalProperties.$socket = socket
    app.mount('#app')
  })
} else {
  socket = initSocket()
  app.config.globalProperties.$socket = socket
  app.mount('#app')
}

if (import.meta.env.DEV) {
  window.$dialog = createDialog
}
