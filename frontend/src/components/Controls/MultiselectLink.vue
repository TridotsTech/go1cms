<template>
  <div>
    <Link
      class="form-control"
      value=""
      :doctype="doctype"
      @change="(option) => addValue(option) && ($refs.input.value = '')"
      :placeholder="placeholder"
      :hideMe="true"
    >
    </Link>
    <div v-if="data?.length" class="mt-3 flex flex-wrap items-center gap-2">
      <Tooltip :text="item.name" v-for="item in data" :key="item.name">
        <Button :label="item.name" theme="gray" variant="outline">
          <template #suffix>
            <FeatherIcon
              class="h-3.5"
              name="x"
              @click.stop="removeValue(item.name)"
            />
          </template>
        </Button>
      </Tooltip>
    </div>
  </div>
</template>

<script setup>
import Link from '@/components/Controls/Link.vue'
import { Tooltip, call } from 'frappe-ui'
const props = defineProps({
  doctype: {
    type: String,
    default: '',
  },
  placeholder: {
    type: String,
    default: __('Lựa chọn'),
  },
})

const data = defineModel()

const removeValue = (value) => {
  data.value = data.value.filter((item) => item.name !== value)
}

const addValue = (value) => {
  if (value) {
    let obj = {
      name: value,
      label: value,
    }
    if (!data.value.find((item) => item.name === value)) {
      data.value.push(obj)
    }
  }
}
</script>
