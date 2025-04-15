<template>
  <Dialog
    v-model="showLanguage"
    :options="{ size: 'lg', position: 'top' }"
    class="z-50"
  >
    <template #body>
      <div>
        <div class="flex flex-col p-2 border-b relative">
          <h1 class="mb-3 px-2 pt-2 text-lg font-semibold text-ink-gray-9">
            {{ __('Select language') }}
          </h1>
          <Button
            class="absolute right-5 top-3.5"
            variant="ghost"
            icon="x"
            @click="showLanguage = false"
          />
        </div>
        <SelectLanguage />
      </div>
    </template>
  </Dialog>
</template>
<script setup>
import {
  defaultLanguage,
  showLanguage,
  changeLanguage,
} from '@/composables/language.js'
import SelectLanguage from '@/components/Settings/SelectLanguage.vue'
import { onMounted } from 'vue'
import { sessionStore } from '@/stores/session'
const { user } = sessionStore()

onMounted(() => {
  if (user) {
    changeLanguage.submit({ lang: defaultLanguage.value })
  }
})
</script>
