import { defineStore } from 'pinia'
import { createResource } from 'frappe-ui'
import { reactive, ref } from 'vue'

export const viewsStore = defineStore('cms-views', (doctype) => {
  // Views
  const views = createResource({
    url: 'go1_cms.api.views.get_views',
    params: { doctype: doctype || '' },
    cache: 'cms-views',
    initialData: [],
    auto: true,
    transform(views) {
      return views
    },
  })

  async function reload() {
    await views.reload()
  }

  return {
    views,
    reload,
  }
})
