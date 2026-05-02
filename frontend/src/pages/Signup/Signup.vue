<template>
    <div class="signup-container">
        <div class="signup-card">
            <h1 class="signup-title">Sign Up</h1>
            <form @submit.prevent="handleSignup" class="signup-form">
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
                    <label for="email">Email</label>
                    <input
                        id="email"
                        v-model="formData.email"
                        type="email"
                        class="form-control"
                        required
                        autocomplete="email"
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
                        autocomplete="new-password"
                    />
                </div>
                <div class="form-group">
                    <label for="passwordConfirm">Confirm Password</label>
                    <input
                        id="passwordConfirm"
                        v-model="formData.passwordConfirm"
                        type="password"
                        class="form-control"
                        required
                        autocomplete="new-password"
                    />
                </div>
                <div class="form-group">
                    <label for="date_of_birth">Date of Birth</label>
                    <input
                        id="date_of_birth"
                        v-model="formData.date_of_birth"
                        type="date"
                        class="form-control"
                        required
                    />
                </div>
                <div class="form-group interests-group">
                    <label>Interests (choose up to 5)</label>
                    <p class="interests-hint">These help us recommend relevant items on your home page.</p>
                    <div v-if="categories.length === 0" class="interests-loading">
                        Loading categories...
                    </div>
                    <div v-else class="interests-grid">
                        <div v-for="group in categories" :key="group.id" class="interest-group">
                            <h4>{{ group.name }}</h4>
                            <div class="interest-options">
                                <label
                                    v-for="child in group.children"
                                    :key="child.id"
                                    class="interest-option"
                                >
                                    <input
                                        type="checkbox"
                                        :value="child.id"
                                        v-model="formData.interests"
                                        :disabled="isInterestDisabled(child.id)"
                                    />
                                    <span>{{ child.name }}</span>
                                </label>
                            </div>
                        </div>
                    </div>
                </div>
                <div v-if="errorMessage" class="alert alert-danger">
                    {{ errorMessage }}
                </div>
                <button type="submit" class="btn btn-primary" :disabled="loading">
                    <span v-if="loading">Creating account...</span>
                    <span v-else>Sign Up</span>
                </button>
            </form>
            <div class="login-link">
                Already have an account? 
                <router-link to="/login">Login here</router-link>
            </div>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import type { SignupForm, CategoryGroup } from '../../types';
import './signup.css';

const router = useRouter();

const formData = reactive<SignupForm>({
    username: '',
    email: '',
    password: '',
    passwordConfirm: '',
    date_of_birth: '',
    interests: [],
});

const loading = ref<boolean>(false);
const errorMessage = ref<string>('');
const categories = ref<CategoryGroup[]>([]);

const validateForm = (): boolean => {
    if (formData.password !== formData.passwordConfirm) {
        errorMessage.value = 'Passwords do not match.';
        return false;
    }
    if (formData.password.length < 8) {
        errorMessage.value = 'Password must be at least 8 characters long.';
        return false;
    }
    if (formData.interests.length > 5) {
        errorMessage.value = 'Please choose up to 5 interests.';
        return false;
    }
    return true;
};

const isInterestDisabled = (id: number): boolean => {
    return formData.interests.length >= 5 && !formData.interests.includes(id);
};

const loadCategories = async (): Promise<void> => {
    try {
        const response = await fetch('/api/categories/', {
            method: 'GET',
        });
        if (!response.ok) return;
        const data = await response.json();
        categories.value = Array.isArray(data.categories) ? data.categories : [];
    } catch (error) {
        console.error('Category load error:', error);
    }
};

const handleSignup = async (): Promise<void> => {
    errorMessage.value = '';
    
    if (!validateForm()) {
        return;
    }

    loading.value = true;

    try {
        // Get CSRF token first
        const csrfResponse = await fetch('/api/csrf-token/', {
            method: 'GET',
            credentials: 'include',
        });
        const csrfData = await csrfResponse.json();
        const csrfToken = csrfData.csrfToken;

        const response = await fetch('/api/signup/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken,
            },
            credentials: 'include',
            body: JSON.stringify({
                username: formData.username,
                email: formData.email,
                password: formData.password,
                date_of_birth: formData.date_of_birth,
                interests: formData.interests,
            }),
        });

        const data = await response.json();

        if (response.ok) {
            // Redirect to login page after successful signup
            router.push({ name: 'Login' });
        } else {
            errorMessage.value = data.error || 'Signup failed. Please try again.';
            if (data.errors) {
                // Handle field-specific errors
                const errorMessages = Object.values(data.errors).flat();
                errorMessage.value = errorMessages.join(', ');
            }
        }
    } catch (error) {
        errorMessage.value = 'An error occurred. Please try again.';
        console.error('Signup error:', error);
    } finally {
        loading.value = false;
    }
};

onMounted(loadCategories);
</script>
