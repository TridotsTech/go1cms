<template>
  <div
    v-if="fieldsComponent && fieldsComponent.length"
    class="p-4 border border-gray-300 rounded-sm mb-4"
  >
    <div class="p-2">
      <div class="mb-4">
        <h2 class="font-bold text-xl">{{ title }}</h2>
      </div>
      <div v-for="(field, idx) in fieldsComponent" :key="field.name">
        <div v-if="field.show_edit" class="border-t py-4">
          <div class="flex flex-wrap justify-between">
            <div class="flex flex-wrap items-center mb-4 gap-4">
              <div class="flex items-center">
                <h2 class="font-bold text-lg">
                  {{ field.section_title }}
                </h2>
                <Tooltip text="Sửa tiêu đề" :hover-delay="1" :placement="'top'">
                  <div>
                    <Button
                      variant="ghost"
                      theme="gray"
                      size="sm"
                      icon="edit"
                      label=""
                    >
                    </Button>
                  </div>
                </Tooltip>
              </div>

              <DialogImage
                :title="field.section_title"
                :urlImage="field.image"
              ></DialogImage>
            </div>
            <!-- tinh nang sau -->
            <!-- <div class="flex items-center mb-4 gap-2">
              <Tooltip
                v-if="field.is_clone"
                text="Xóa nhân bản"
                :hover-delay="1"
                :placement="'top'"
              >
                <Button variant="outline" theme="red" size="sm" label="Xóa">
                </Button>
              </Tooltip>
              <Tooltip
                v-if="field.allow_clone"
                text="Nhân bản thành phần"
                :hover-delay="1"
                :placement="'top'"
              >
                <Button
                  variant="outline"
                  theme="blue"
                  size="sm"
                  label="Nhân bản"
                >
                </Button>
              </Tooltip>
            </div> -->
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
            <template v-for="fd in field.fields_ps">
              <FieldSection :field="fd"></FieldSection>
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
    default: 'Các thành phần của trang',
  },
})
const fieldsComponent = defineModel()
</script>
