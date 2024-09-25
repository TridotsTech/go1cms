import { createRouter, createWebHistory } from 'vue-router'
import { userResource } from '@/stores/user'
import { sessionStore } from '@/stores/session'

const routes = [
  {
    path: '/',
    redirect: { name: 'Interface Repository' },
    name: 'Home',
  },
  // {
  //   path: '/my-website',
  //   name: 'My Website',
  //   component: () => import('@/pages/MyWebsite.vue'),
  // },
  {
    path: '/interface-repository',
    name: 'Interface Repository',
    component: () => import('@/pages/InterfaceRepository.vue'),
  },
  {
    path: '/interface-repository/:interfaceId',
    name: 'Interface Template',
    component: () => import('@/pages/InterfaceTemplate.vue'),
    props: true,
  },
  {
    path: '/interface',
    name: 'Interface',
    component: () => import('@/pages/Interface.vue'),
  },
  {
    path: '/domain',
    name: 'Domain',
    component: () => import('@/pages/Domain.vue'),
  },
  {
    path: '/website-setup',
    name: 'Website Setup',
    component: () => import('@/pages/WebsiteSetup.vue'),
  },
  {
    path: '/setup-file-template',
    name: 'Setup File Template',
    component: () => import('@/pages/SetupFileTemplate.vue'),
  },
  {
    path: '/form-setup',
    name: 'Form Setup',
    component: () => import('@/pages/FormSetup.vue'),
  },
  {
    path: '/contacts',
    name: 'Contacts',
    component: () => import('@/pages/contact/Contacts.vue'),
  },
  {
    path: '/contacts/:contactId',
    name: 'Contact Detail',
    component: () => import('@/pages/contact/ContactDetail.vue'),
    props: true,
  },
  {
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/pages/Dashboard.vue'),
  },
  {
    path: '/page',
    name: 'Page',
    component: () => import('@/pages/Page.vue'),
  },
  {
    path: '/new-page',
    name: 'New Page',
    component: () => import('@/pages/NewPage.vue'),
  },
  {
    path: '/header-page',
    name: 'Header Page',
    component: () => import('@/pages/HeaderPage.vue'),
  },
  {
    path: '/footer-page',
    name: 'Footer Page',
    component: () => import('@/pages/FooterPage.vue'),
  },
  {
    path: '/posts',
    name: 'Posts',
    component: () => import('@/pages/post/Posts.vue'),
  },
  {
    path: '/posts/create',
    name: 'Post Create',
    component: () => import('@/pages/post/PostCreate.vue'),
  },
  {
    path: '/posts/:postId',
    name: 'Post Detail',
    component: () => import('@/pages/post/PostDetail.vue'),
    props: true,
  },
  {
    path: '/categories',
    name: 'Categories',
    component: () => import('@/pages/category/Categories.vue'),
  },
  {
    path: '/categories/create',
    name: 'Category Create',
    component: () => import('@/pages/category/CategoryCreate.vue'),
  },
  {
    path: '/categories/:categoryId',
    name: 'Category Detail',
    component: () => import('@/pages/category/CategoryDetail.vue'),
    props: true,
  },
  {
    path: '/blog-tags',
    name: 'Blog Tags',
    component: () => import('@/pages/BlogTag/Tags.vue'),
  },
  {
    path: '/blog-tags/create',
    name: 'Blog Tags Create',
    component: () => import('@/pages/BlogTag/TagCreate.vue'),
  },
  {
    path: '/blog-tags/:tagId',
    name: 'Blog Tags Detail',
    component: () => import('@/pages/BlogTag/TagDetail.vue'),
    props: true,
  },
  {
    path: '/menu',
    name: 'Menu',
    component: () => import('@/pages/menu/Menu.vue'),
  },
  {
    path: '/menu/create',
    name: 'Menu Create',
    component: () => import('@/pages/menu/MenuCreate.vue'),
  },
  {
    path: '/menu/:menuId',
    name: 'Menu Detail',
    component: () => import('@/pages/menu/MenuDetail.vue'),
    props: true,
  },
  {
    path: '/forms',
    name: 'Forms',
    component: () => import('@/pages/form/Forms.vue'),
  },
  {
    path: '/forms/:formId',
    name: 'Form Detail',
    component: () => import('@/pages/form/FormDetail.vue'),
    props: true,
  },
  {
    path: '/:invalidpath',
    name: 'Invalid Page',
    component: () => import('@/pages/InvalidPage.vue'),
  },
  {
    path: '/permission-denied',
    name: 'Permission Denied Page',
    component: () => import('@/pages/PermissionDeniedPage.vue'),
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/Login.vue'),
  },
]

const scrollBehavior = (to, from, savedPosition) => {
  if (to.name === from.name) {
    to.meta?.scrollPos && (to.meta.scrollPos.top = 0)
    return { left: 0, top: 0 }
  }
  const scrollpos = to.meta?.scrollPos || { left: 0, top: 0 }

  if (scrollpos.top > 0) {
    setTimeout(() => {
      let el = document.querySelector('#list-rows')
      el.scrollTo({
        top: scrollpos.top,
        left: scrollpos.left,
        behavior: 'smooth',
      })
    }, 300)
  }
}

let router = createRouter({
  history: createWebHistory('/cms'),
  routes,
  scrollBehavior,
})

router.beforeEach(async (to, from, next) => {
  const { isLoggedIn, isSystemUser } = sessionStore()

  isLoggedIn && (await userResource.promise)

  if (from.meta?.scrollPos) {
    from.meta.scrollPos.top = document.querySelector('#list-rows')?.scrollTop
  }

  if (to.name === 'Login' && isLoggedIn) {
    next({ name: 'Interface Repository' })
  } else if (to.name !== 'Login' && !isLoggedIn) {
    next({ name: 'Login' })
  } else if (
    isLoggedIn &&
    !isSystemUser &&
    !['Permission Denied Page', 'Invalid Page'].includes(to.name)
  ) {
    next({ name: 'Permission Denied Page' })
  } else if (to.matched.length === 0) {
    next({ name: 'Invalid Page' })
  } else {
    next()
  }
})

export default router
