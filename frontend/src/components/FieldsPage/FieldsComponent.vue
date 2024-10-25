<template>
  <div
    v-if="fieldsComponent && fieldsComponent?.length"
    class="p-4 border border-gray-300 rounded-sm mb-4"
  >
    <div class="p-2">
      <div class="mb-4">
        <h2 class="font-bold text-xl">{{ title }}</h2>
      </div>
      <div v-for="(field, idx) in fieldsComponent" :key="field.name">
        <div v-if="field.show_edit" class="border-t py-4">
          <div class="flex items-center mb-4 gap-4">
            <div>
              <h2 class="font-bold text-lg">{{ field.section_title }}</h2>
              <div
                v-if="field.description && field.description?.msg"
                class="text-base mt-2 flex gap-2"
                :class="getStatusDescription(field.description?.type)"
              >
                <FeatherIcon
                  name="alert-triangle"
                  class="h-4 transition-all duration-300 ease-in-out"
                  :class="getStatusDescription(field.description?.type)"
                />
                {{ field.description?.msg }}
              </div>
            </div>
            <DialogImage
              v-if="field.show_prv_image"
              :title="field.section_title"
              :urlImage="field.image"
            ></DialogImage>
          </div>
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <template v-for="fd in field.fields">
              <template v-if="fd.group_name && fd.show_edit">
                <div class="lg:col-span-2">
                  <div
                    v-if="fd.section_title"
                    class="text-base text-gray-700 font-bold mb-2"
                  >
                    {{ fd.section_title }}
                  </div>
                  <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
                    <template v-for="fsc in fd.fields">
                      <FieldSection
                        :field="fsc"
                        :sectionName="field.section_title"
                      ></FieldSection>
                    </template>
                  </div>
                </div>
              </template>
              <template v-else>
                <FieldSection
                  :field="fd"
                  :sectionName="field.section_title"
                ></FieldSection>
              </template>
            </template>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import FieldSection from '@/components/FieldSection.vue'
import DialogImage from '@/components/DialogImage.vue'

const props = defineProps({
  title: {
    type: String,
    default: 'Thông tin chung',
  },
})
const fieldsComponent = defineModel()

function getStatusDescription(type) {
  switch (type) {
    case 'warn':
      return 'text-orange-500'
    default:
      return 'text-gray-700'
  }
}
</script>
