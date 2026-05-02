import { createRouter, createWebHistory } from 'vue-router';

import Landing from '../pages/Landing/Landing.vue';
import Login from '../pages/Login/Login.vue';
import Signup from '../pages/Signup/Signup.vue';

import MainLayout from '../layouts/MainLayout.vue';
import Main from '../pages/Main/Main.vue';
import Profile from '../pages/Profile/Profile.vue';
import Items from '../pages/Items/Items.vue';
import ItemDetail from '../pages/ItemDetail.vue';
import ListItem from '../pages/ListItem/ListItem.vue';

const base = import.meta.env.MODE === 'development' ? import.meta.env.BASE_URL : '';

const router = createRouter({
  history: createWebHistory(base),
  routes: [
    { path: '/', name: 'Landing', component: Landing },
    { path: '/login', name: 'Login', component: Login },
    { path: '/signup', name: 'Signup', component: Signup },

    {
      path: '/main',
      component: MainLayout,
      children: [
        { path: '', name: 'Main', component: Main },
        { path: 'profile', name: 'Profile', component: Profile },
        { path: 'items', name: 'Items', component: Items },
        { path: 'items/:id', name: 'ItemDetail', component: ItemDetail },
        { path: 'list-item', name: 'ListItem', component: ListItem },
      ],
    },
  ],
});

export default router;