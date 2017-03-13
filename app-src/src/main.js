import Vue from 'vue'
import VueRouter from 'vue-router'
import VueResource from 'vue-resource'
import store from './store/store'
import {
  Placeable,
  CalibrateInstrument,
  App
} from './components/export'

Vue.use(VueRouter)
Vue.use(VueResource)

const router = new VueRouter({
  routes: [
    { path: '/calibrate/:instrument', component: CalibrateInstrument },
    { path: '/calibrate/:instrument/:placeable', component: Placeable }
  ],
  mode: 'history'
})

/* eslint-disable */
window.onload = function () {
  // Google analytics SPA extensions: https://github.com/googleanalytics/autotrack
  require('autotrack')
  window.ga('require', 'eventTracker')
  window.ga('require', 'outboundLinkTracker')
  window.ga('require', 'urlChangeTracker')

  const app = new Vue({
    router,
    store,
    ...App
  }).$mount('#app')
}
/* eslint-enable */
