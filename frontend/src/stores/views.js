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
    transform(views) {
      for (let view of views.views) {
        viewsByName[view.name] = view
        if (view.is_default && view.dt) {
          defaultView.value[view.dt] = view
        }
      }
      return views
    },
  })

  function getView(view, doctype = null) {
    if (!view && doctype) {
      return defaultView.value?.[doctype] || null
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
