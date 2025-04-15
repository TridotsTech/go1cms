<template>
  <div class="flex flex-1 flex-col overflow-y-auto mb-4 px-4 pt-3">
    <Autocomplete
      class="border-2 rounded-md border-gray-300"
      :options="optionsLanguage"
      v-model="single"
      placeholder="Select language"
      :hideSearch="true"
    >
      <template #prefix>
        <img :src="single.image" class="mr-2 h-4.5 w-7" />
      </template>
      <template #item-prefix="{ option }">
        <img :src="option.image.toString()" class="h-4.5 w-7 mr-2" />
      </template>
    </Autocomplete>
  </div>
</template>
<script setup>
import {
  defaultLanguage,
  fetchLanguage,
  changeLanguage,
} from '@/composables/language.js'
import { Autocomplete } from 'frappe-ui'
import { ref, watch, onMounted } from 'vue'
import { sessionStore } from '@/stores/session'
const { user } = sessionStore()

const optionsLanguage = ref([
  {
    label: __('Vietnamese'),
    value: 'vi',
    image: '/assets/go1_cms/images/icon_flag_vi.svg',
  },
  {
    label: __('English'),
    value: 'en',
    image: '/assets/go1_cms/images/icon_flag_en.svg',
  },
])
const single = ref()

onMounted(() => {
  let lang = localStorage.getItem('lang')
  if (user && !lang) {
    fetchLanguage.fetch()
  }
})

const setDefaultLanguage = (lang) => {
  localStorage.setItem('lang', lang)
  defaultLanguage.value = lang
}

watch(
  defaultLanguage,
  (val) => {
    single.value = optionsLanguage.value.find((item) => item.value === val)
  },
  {
    immediate: true,
  },
)

watch(single, (val) => {
  if (val.value === defaultLanguage.value) return

  setDefaultLanguage(val.value)
  if (user) {
    changeLanguage.submit(
      { lang: val.value },
      {
        onSuccess: () => {
          window.location.reload()
        },
      },
    )
  } else {
    window.location.reload()
  }
})
</script>
