<template>
  <div class="quill-fullscreen bg-white z-50">
    <!-- <QuillEditor
      :class="classQuill + ' ' + classHeightscreen"
      theme="snow"
      :toolbar="toolbar"
      v-model:content="content"
      :contentType="contentType"
    ></QuillEditor> -->
    <TextEditor
      variant="outline"
      editor-class="!prose-sm overflow-auto min-h-[180px] max-h-80 py-1.5 px-2 border border-gray-300 bg-white hover:border-gray-400 hover:shadow-sm focus:bg-white focus:border-gray-500 focus:shadow-sm focus:ring-0 focus-visible:ring-2 focus-visible:ring-gray-400 text-gray-800 transition-colors min-w-full"
      fixedMenu="true"
      :content="content"
      @change="(val) => (content = val)"
    ></TextEditor>
  </div>
</template>

<script setup>
// import { QuillEditor } from '@vueup/vue-quill'
// import '@vueup/vue-quill/dist/vue-quill.snow.css'
import { onMounted } from 'vue'
import { api as fullscreen } from 'vue-fullscreen'
import { TextEditor } from 'frappe-ui'

const props = defineProps({
  classHeightscreen: {
    type: String,
    default: 'max-h-80',
  },
  classQuill: {
    type: String,
    default: '',
  },
  contentType: {
    type: String,
    default: 'html',
  },
  toolbar: {
    type: Array,
    default: [
      ['bold', 'italic', 'underline', 'strike'], // toggled buttons
      ['blockquote', 'code-block'],
      ['link', 'image', 'video', 'formula'],

      [{ header: 1 }, { header: 2 }], // custom button values
      [{ list: 'ordered' }, { list: 'bullet' }, { list: 'check' }],
      [{ script: 'sub' }, { script: 'super' }], // superscript/subscript
      [{ indent: '-1' }, { indent: '+1' }], // outdent/indent
      [{ direction: 'rtl' }], // text direction

      [{ size: ['small', false, 'large', 'huge'] }], // custom dropdown
      [{ header: [1, 2, 3, 4, 5, 6, false] }],

      [{ color: [] }, { background: [] }], // dropdown with defaults from theme
      [{ font: [] }],
      [{ align: [] }],

      ['clean'], // remove formatting button
      ['fullscreen'],
      ['table'],
    ],
  },
})

const content = defineModel()

// onMounted(() => {
//   var customButton = document.querySelector('.ql-fullscreen')
//   var svgStr =
//     '<svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><g id="SVGRepo_bgCarrier" stroke-width="0"></g><g id="SVGRepo_tracerCarrier" stroke-linecap="round" stroke-linejoin="round"></g><g id="SVGRepo_iconCarrier"> <path fill-rule="evenodd" clip-rule="evenodd" d="M3 4C3 3.44772 3.44772 3 4 3H8C8.55228 3 9 3.44772 9 4C9 4.55228 8.55228 5 8 5H6.41421L9.70711 8.29289C10.0976 8.68342 10.0976 9.31658 9.70711 9.70711C9.31658 10.0976 8.68342 10.0976 8.29289 9.70711L5 6.41421V8C5 8.55228 4.55228 9 4 9C3.44772 9 3 8.55228 3 8V4ZM16 3H20C20.5523 3 21 3.44772 21 4V8C21 8.55228 20.5523 9 20 9C19.4477 9 19 8.55228 19 8V6.41421L15.7071 9.70711C15.3166 10.0976 14.6834 10.0976 14.2929 9.70711C13.9024 9.31658 13.9024 8.68342 14.2929 8.29289L17.5858 5H16C15.4477 5 15 4.55228 15 4C15 3.44772 15.4477 3 16 3ZM9.70711 14.2929C10.0976 14.6834 10.0976 15.3166 9.70711 15.7071L6.41421 19H8C8.55228 19 9 19.4477 9 20C9 20.5523 8.55228 21 8 21H4C3.44772 21 3 20.5523 3 20V16C3 15.4477 3.44772 15 4 15C4.55228 15 5 15.4477 5 16V17.5858L8.29289 14.2929C8.68342 13.9024 9.31658 13.9024 9.70711 14.2929ZM14.2929 14.2929C14.6834 13.9024 15.3166 13.9024 15.7071 14.2929L19 17.5858V16C19 15.4477 19.4477 15 20 15C20.5523 15 21 15.4477 21 16V20C21 20.5523 20.5523 21 20 21H16C15.4477 21 15 20.5523 15 20C15 19.4477 15.4477 19 16 19H17.5858L14.2929 15.7071C13.9024 15.3166 13.9024 14.6834 14.2929 14.2929Z" fill="#000000"></path> </g></svg>'
//   customButton.innerHTML = svgStr

//   customButton.addEventListener('click', async function () {
//     let parentElement = this.closest('.quill-fullscreen')
//     await fullscreen.toggle(parentElement, {
//       teleport: false,
//       pageOnly: true,
//       callback: (isFullscreen) => {
//         let arr = props.classHeightscreen.split(' ')
//         let elmContainer = parentElement.querySelector('.ql-container')
//         let elmToolbar = parentElement.querySelector('.ql-toolbar')
//         if (isFullscreen) {
//           elmContainer.style.maxHeight = `calc(100% - ${elmToolbar.offsetHeight}px)`
//           elmContainer.classList.remove(...arr)
//         } else {
//           elmContainer.style.maxHeight = ''
//           elmContainer.classList.add(...arr)
//         }
//       },
//     })
//   })
// })
</script>
