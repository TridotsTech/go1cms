<template>
  <div
    v-if="page?.fields_cp && page?.fields_cp.length"
    class="p-4 border border-gray-300 rounded-sm mb-4"
  >
    <div class="p-2">
      <div class="mb-4">
        <h2 class="font-bold text-xl">Thông tin chung</h2>
      </div>
      <div v-for="(field, idx) in page?.fields_cp" :key="field.name">
        <div v-if="field.show_edit" class="border-t py-4">
          <div class="mb-4">
            <h2 class="font-bold text-lg">{{ field.section_title }}</h2>
          </div>
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <template v-for="fd in field.fields">
              <template v-if="fd.group_name">
                <div class="lg:col-span-2">
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

const page = defineModel()
</script>
