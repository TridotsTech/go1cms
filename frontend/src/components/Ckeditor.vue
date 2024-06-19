<template>
  <ckeditor :editor="editor" v-model="data" :config="editorConfig"></ckeditor>
</template>

<script setup>
import { ClassicEditor } from '@ckeditor/ckeditor5-editor-classic'
import {
  Bold,
  Code,
  Italic,
  Strikethrough,
  Subscript,
  Superscript,
  Underline,
} from '@ckeditor/ckeditor5-basic-styles'
import { Paragraph } from '@ckeditor/ckeditor5-paragraph'
import { Essentials } from '@ckeditor/ckeditor5-essentials'
import { Heading } from '@ckeditor/ckeditor5-heading'
import {
  Table,
  TableCaption,
  TableCellProperties,
  TableColumnResize,
  TableProperties,
  TableToolbar,
} from '@ckeditor/ckeditor5-table'
import {
  AutoImage,
  Image,
  ImageCaption,
  ImageInsert,
  ImageResize,
  ImageStyle,
  ImageToolbar,
  ImageUpload,
  PictureEditing,
} from '@ckeditor/ckeditor5-image'
import { SourceEditing } from '@ckeditor/ckeditor5-source-editing'
import { BlockQuote } from '@ckeditor/ckeditor5-block-quote'
import { AutoLink, Link, LinkImage } from '@ckeditor/ckeditor5-link'
import { CodeBlock } from '@ckeditor/ckeditor5-code-block'
import { RemoveFormat } from '@ckeditor/ckeditor5-remove-format'
import { HorizontalLine } from '@ckeditor/ckeditor5-horizontal-line'
import {
  SpecialCharacters,
  SpecialCharactersEssentials,
} from '@ckeditor/ckeditor5-special-characters'
import { CKBox, CKBoxImageEdit } from '@ckeditor/ckeditor5-ckbox'
import { CloudServices } from '@ckeditor/ckeditor5-cloud-services'
import { Font } from '@ckeditor/ckeditor5-font'
import { Highlight } from '@ckeditor/ckeditor5-highlight'
import { Alignment } from '@ckeditor/ckeditor5-alignment'
import { HtmlEmbed } from '@ckeditor/ckeditor5-html-embed'
import { TextTransformation } from '@ckeditor/ckeditor5-typing'
import { List, ListProperties, TodoList } from '@ckeditor/ckeditor5-list'
import { Indent, IndentBlock } from '@ckeditor/ckeditor5-indent'
import { MediaEmbed } from '@ckeditor/ckeditor5-media-embed'
import { Base64UploadAdapter } from '@ckeditor/ckeditor5-upload'
import '@ckeditor/ckeditor5-build-classic/build/translations/vi'

const props = defineProps({
  placeholder: String,
})

const data = defineModel()

const editor = ClassicEditor
const editorConfig = {
  plugins: [
    Base64UploadAdapter,
    MediaEmbed,
    Indent,
    IndentBlock,
    List,
    ListProperties,
    TodoList,
    TextTransformation,
    HtmlEmbed,
    Essentials,
    Bold,
    Code,
    Italic,
    Strikethrough,
    Subscript,
    Superscript,
    Underline,
    AutoLink,
    Link,
    LinkImage,
    Paragraph,
    Heading,
    Table,
    TableCaption,
    TableCellProperties,
    TableColumnResize,
    TableProperties,
    TableToolbar,
    SourceEditing,
    BlockQuote,
    AutoImage,
    Image,
    ImageCaption,
    ImageInsert,
    ImageResize,
    ImageStyle,
    ImageToolbar,
    ImageUpload,
    PictureEditing,
    CodeBlock,
    RemoveFormat,
    HorizontalLine,
    SpecialCharacters,
    SpecialCharactersEssentials,
    CKBox,
    CKBoxImageEdit,
    CloudServices,
    Font,
    Highlight,
    Alignment,
  ],
  toolbar: {
    items: [
      'undo',
      'redo',
      '|',
      'heading',
      '|',
      'fontSize',
      'fontFamily',
      'fontColor',
      'fontBackgroundColor',
      // {
      //   label: 'Font color',
      //   icon: 'plus',
      //   items: ['fontColor', 'fontBackgroundColor'],
      // },
      '|',
      'bold',
      'italic',
      'underline',
      {
        label: 'Formatting',
        icon: 'text',
        items: [
          'strikethrough',
          'subscript',
          'superscript',
          'code',
          'horizontalLine',
          '|',
          'removeFormat',
        ],
      },
      'specialCharacters',
      '|',
      'link',
      'insertImage',
      'insertTable',
      {
        label: 'Insert',
        icon: 'plus',
        items: [
          'highlight',
          'blockQuote',
          'mediaEmbed',
          'codeBlock',
          'htmlEmbed',
        ],
      },
      '|',
      'alignment',
      '|',
      'bulletedList',
      'numberedList',
      'todoList',
      'outdent',
      'indent',
      '|',
      'sourceEditing',
    ],
  },
  fontFamily: {
    supportAllValues: true,
  },
  fontSize: {
    options: [
      'default',
      10,
      11,
      12,
      13,
      14,
      15,
      16,
      18,
      20,
      21,
      22,
      24,
      26,
      28,
      32,
      36,
      40,
      42,
      44,
      48,
    ],
    supportAllValues: true,
  },
  image: {
    styles: ['alignCenter', 'alignLeft', 'alignRight'],
    resizeOptions: [
      {
        name: 'resizeImage:original',
        label: 'Original',
        value: null,
      },
      {
        name: 'resizeImage:50',
        label: '50%',
        value: '50',
      },
      {
        name: 'resizeImage:75',
        label: '75%',
        value: '75',
      },
    ],
    toolbar: [
      'imageTextAlternative',
      'toggleImageCaption',
      '|',
      'imageStyle:inline',
      'imageStyle:wrapText',
      'imageStyle:breakText',
      '|',
      'resizeImage',
      '|',
      'ckboxImageEdit',
    ],
  },
  list: {
    properties: {
      styles: true,
      startIndex: true,
      reversed: true,
    },
  },
  link: {
    decorators: {
      addTargetToExternalLinks: true,
      defaultProtocol: 'https://',
      toggleDownloadable: {
        mode: 'manual',
        label: 'Downloadable',
        attributes: {
          download: 'file',
        },
      },
    },
  },
  table: {
    contentToolbar: [
      'tableColumn',
      'tableRow',
      'mergeTableCells',
      'tableProperties',
      'tableCellProperties',
      'toggleTableCaption',
    ],
  },
  language: 'vi',
}
</script>
<style>
.ck.ck-editor__editable_inline {
  padding-bottom: 40px;
}
.ck-content .image-inline.image-style-align-left {
  margin-right: var(--ck-image-style-spacing);
}
.ck-content .image-inline.image-style-align-right {
  margin-left: var(--ck-image-style-spacing);
}
.ck-content .image-inline.image-style-align-left,
.ck-content .image-inline.image-style-align-right {
  margin-top: inherit;
  margin-bottom: inherit;
}
</style>
