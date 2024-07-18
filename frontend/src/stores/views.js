import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'
import { reactive, ref } from 'vue'

export const viewsStore = defineStore('cms-views', (doctype) => {
  let defaultView = ref({})
  let viewsByName = reactive({})

  // Views
  const views = createResource({
    url: 'go1_cms.api.views.get_views',
    params: { doctype: doctype || '' },
    cache: 'cms-views',
    initialData: [],
    auto: true,
    transform(data) {
      for (let view of data.views) {
        viewsByName[view.name] = view
        if (view.is_default && view.dt) {
          defaultView.value[view.dt + ' ' + view.type] = view
        }
      }
      return data
    },
  })

  function getView(view, type, doctype = null) {
    type = type || 'list'
    if (!view && doctype) {
      return defaultView.value[doctype + ' ' + type] || null
    }
    return viewsByName[view]
  }

  async function reload() {
    await views.reload()
  }

  return {
    views,
    defaultView,
    reload,
    getView,
  }
})
