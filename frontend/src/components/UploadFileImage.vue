<template>
  <div class="grid lg:grid-cols-2 gap-4">
    <div>
      <label v-if="title" class="block text-base text-gray-600 mb-2">
        {{ title }}
      </label>
      <Button
        iconLeft="paperclip"
        label="Upload ảnh"
        @click="$refs.refFile.click()"
      ></Button>
      <input
        ref="refFile"
        class="hidden"
        type="file"
        accept="image/*"
        @change="(e) => validateFile(e.target.files)"
      />
      <div v-if="nameFile" class="text-sm my-2">{{ nameFile }}</div>
      <ErrorMessage v-if="messageError" class="my-1" :message="messageError" />
    </div>
    <slot name="preview"></slot>
  </div>
</template>

<script setup>
import { ErrorMessage } from 'frappe-ui'
import { ref, watch } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: 'Ảnh',
  },
})

const refImg = defineModel('refImg')
const inputFile = defineModel()
const messageError = ref()
const nameFile = ref()

watch(inputFile, (val) => {
  if (!val) {
    nameFile.value = ''
  }
})

const reader = new FileReader()
reader.addEventListener(
  'load',
  () => {
    refImg.value.src = reader.result
  },
  false
)

function validateFile(files) {
  if (files && files[0]) {
    let file = files[0]
    let extn = file.name.split('.').pop().toLowerCase()
    if (!['png', 'jpg', 'jpeg'].includes(extn)) {
      messageError.value = 'Chỉ cho phép hình ảnh PNG và JPG'
    }
    inputFile.value = file
    nameFile.value = file.name
    reader.readAsDataURL(file)
  }
}
</script>
