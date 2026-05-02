<template>
    <div class="login-container">
        <div class="login-card">
            <h1 class="login-title">Login</h1>
            <form @submit.prevent="handleLogin" class="login-form">
                <div class="form-group">
                    <label for="username">Username</label>
                    <input
                        id="username"
                        v-model="formData.username"
                        type="text"
                        class="form-control"
                        required
                        autocomplete="username"
                    />
                </div>
                <div class="form-group">
                    <label for="password">Password</label>
                    <input
                        id="password"
                        v-model="formData.password"
                        type="password"
                        class="form-control"
                        required
                        autocomplete="current-password"
                    />
                </div>
                <div v-if="errorMessage" class="alert alert-danger">
                    {{ errorMessage }}
                </div>
                <button type="submit" class="btn btn-primary" :disabled="loading">
                    <span v-if="loading">Logging in...</span>
                    <span v-else>Login</span>
                </button>
            </form>
            <div class="signup-link">
                Don't have an account? 
                <router-link to="/signup">Sign up here</router-link>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/stores';
import type { LoginForm } from '../../types';
import './login.css';

const router = useRouter();
const userStore = useUserStore();

const formData = reactive<LoginForm>({
    username: '',
    password: '',
});

const loading = ref<boolean>(false);
const errorMessage = ref<string>('');

const handleLogin = async (): Promise<void> => {
    errorMessage.value = '';
    loading.value = true;

    try {
        const result = await userStore.login(formData.username, formData.password);

        if (result.success) {
            router.push({ name: 'Main' });
        } else {
            errorMessage.value = result.error || 'Login failed. Please check your credentials.';
        }
    } catch (error) {
        errorMessage.value = 'An error occurred. Please try again.';
        console.error('Login error:', error);
    } finally {
        loading.value = false;
    }
};
</script>