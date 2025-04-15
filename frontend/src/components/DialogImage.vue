<template>
  <Tooltip :text="__('View sample image')" :hover-delay="1" :placement="'top'">
    <div>
      <Button
        variant="subtle"
        theme="blue"
        size="sm"
        icon="eye"
        @click="() => handleShow()"
      >
      </Button>
    </div>
  </Tooltip>
  <Dialog v-model="showPreviewImage" :options="{ size: '4xl' }">
    <template #body-title>
      <h3>{{ __(title) }}</h3>
    </template>
    <template #body-content>
      <div class="flex justify-center">
        <img class="max-w-full" :src="urlImage || noImage" alt="" />
      </div>
    </template>
  </Dialog>
</template>

<script setup>
import noImage from '@/assets/images/no_image.jpg'
import { ref } from 'vue'

const props = defineProps({
  title: {
    type: String,
    default: '',
  },
  urlImage: {
    type: String,
    default: undefined,
  },
})

const showPreviewImage = ref(false)

function handleShow() {
  showPreviewImage.value = true
}
</script>
