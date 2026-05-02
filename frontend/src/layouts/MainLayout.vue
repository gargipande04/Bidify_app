<template>
    <div class="layout-wrapper">
        <nav class="main-navbar">
            <div class="navbar-container">
                <div class="navbar-brand">
                    <router-link to="/main" class="brand-link">
                        <span class="brand-text">Bidify</span>
                    </router-link>
                </div>
                <div class="navbar-tabs">
                    <router-link
                        class="nav-tab"
                        :class="{ active: $route.name === 'Main' }"
                        :to="{ name: 'Main' }"
                    >
                        Home
                    </router-link>
                    <router-link
                        class="nav-tab"
                        :class="{ active: $route.name === 'Items' }"
                        :to="{ name: 'Items' }"
                    >
                        Items
                    </router-link>
                    <router-link
                        class="nav-tab"
                        :class="{ active: $route.name === 'ListItem' }"
                        :to="{ name: 'ListItem' }"
                    >
                        List Item
                    </router-link>
                    <router-link
                        class="nav-tab"
                        :class="{ active: $route.name === 'Profile' }"
                        :to="{ name: 'Profile' }"
                    >
                        {{ userStore.username || 'Profile' }}
                    </router-link>
                    <button class="nav-tab logout-tab" @click="handleLogout">
                        Logout
                    </button>
                </div>
            </div>
        </nav>
        <main class="layout-content">
            <router-view />
        </main>
    </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores';

const router = useRouter();
const userStore = useUserStore();

const handleLogout = async () => {
    await userStore.logout();
    router.push({ name: 'Login' });
};
</script>

<style scoped>
.layout-wrapper {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

.main-navbar {
    background-color: #1a1a2e;
    padding: 0;
    position: sticky;
    top: 0;
    z-index: 1000;
}

.navbar-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 64px;
}

.navbar-brand {
    display: flex;
    align-items: center;
}

.brand-link {
    text-decoration: none;
}

.brand-text {
    font-size: 1.4rem;
    font-weight: 700;
    color: #fff;
}

.navbar-tabs {
    display: flex;
    align-items: center;
    gap: 8px;
}

.nav-tab {
    text-decoration: none;
    color: #a0a0b0;
    font-weight: 500;
    padding: 10px 20px;
    border-radius: 8px;
    transition: all 0.2s ease;
}

.nav-tab:hover {
    color: #fff;
    background-color: rgba(255, 255, 255, 0.1);
}

.nav-tab.active {
    color: #fff;
    background-color: #007bff;
}

.logout-tab {
    border: none;
    cursor: pointer;
    background-color: transparent;
    font-size: 1rem;
}

.logout-tab:hover {
    background-color: #dc3545;
    color: #fff;
}

.layout-content {
    flex: 1;
    max-width: 1200px;
    width: 100%;
    margin: 0 auto;
    padding: 20px;
}

@media (max-width: 768px) {
    .navbar-container {
        flex-direction: column;
        height: auto;
        padding: 15px 20px;
        gap: 15px;
    }

    .navbar-tabs {
        width: 100%;
        justify-content: center;
        flex-wrap: wrap;
    }

    .nav-tab {
        padding: 8px 14px;
        font-size: 0.9rem;
    }
}
</style>
