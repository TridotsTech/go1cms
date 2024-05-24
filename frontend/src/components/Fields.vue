<template>
  <div class="flex flex-col gap-4">
    <div
      v-for="section in sections"
      :key="section.section"
      class="first:border-t-0 first:pt-0"
      :class="section.hideBorder ? '' : 'border-t pt-4'"
    >
      <div
        class="grid gap-4"
        :class="
          (section.columns ? 'grid-cols-' + section.columns : 'grid-cols-3') +
          ' ' +
          section.class
        "
      >
        <div
          v-for="field in section.fields"
          :key="field.typeArray ? field.section : field.name"
        >
          <div v-if="field.typeArray == true">
            <div class="grid gap-4 grid-cols-1">
              <div v-for="fc in field.fields" :key="fc.name">
                <Field
                  :field="fc"
                  :imgPreview="data[fc?.imgPreview]"
                  v-model="data[fc.name]"
                ></Field>
              </div>
            </div>
          </div>
          <Field
            v-else
            :field="field"
            :imgPreview="data[field?.imgPreview]"
            v-model="data[field.name]"
          ></Field>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import Field from '@/components/Field.vue'

const props = defineProps({
  sections: Array,
  data: Object,
})
</script>

<style scoped>
:deep(.form-control.prefix select) {
  padding-left: 2rem;
}
</style>
