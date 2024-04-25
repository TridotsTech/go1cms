import { createRouter, createWebHistory } from 'vue-router'
import { usersStore } from '@/stores/users'
import { sessionStore } from '@/stores/session'

const routes = [
  {
    path: '/',
    redirect: { name: 'My Website' },
    name: 'Home',
  },
  {
    path: '/my-website',
    name: 'My Website',
    component: () => import('@/pages/MyWebsite.vue'),
  },
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
    path: '/dashboard',
    name: 'Dashboard',
    component: () => import('@/pages/Dashboard.vue'),
  },
  {
    path: '/:invalidpath',
    name: 'Invalid Page',
    component: () => import('@/pages/InvalidPage.vue'),
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
  const { users } = usersStore()
  const { isLoggedIn } = sessionStore()

  isLoggedIn && (await users.promise)

  if (from.meta?.scrollPos) {
    from.meta.scrollPos.top = document.querySelector('#list-rows')?.scrollTop
  }

  if (to.name === 'Login' && isLoggedIn) {
    next({ name: 'Leads' })
  } else if (to.name !== 'Login' && !isLoggedIn) {
    next({ name: 'Login' })
  } else if (to.matched.length === 0) {
    next({ name: 'Invalid Page' })
  } else {
    next()
  }
})

export default router
