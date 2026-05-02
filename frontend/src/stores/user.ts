import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useUserStore = defineStore('user', () => {
    const username = ref<string | null>(null);
    const isLoading = ref(false);

    const isLoggedIn = computed(() => username.value !== null);

    async function fetchUser() {
        isLoading.value = true;
        try {
            const response = await fetch('/api/me/', {
                credentials: 'include',
            });
            if (response.ok) {
                const data = await response.json();
                username.value = data.username;
            } else {
                username.value = null;
            }
        } catch {
            username.value = null;
        } finally {
            isLoading.value = false;
        }
    }

    async function login(usernameInput: string, password: string): Promise<{ success: boolean; error?: string }> {
        try {
            // Get CSRF token
            const csrfResponse = await fetch('/api/csrf-token/', {
                credentials: 'include',
            });
            const csrfData = await csrfResponse.json();
            const csrfToken = csrfData.csrfToken;

            const response = await fetch('/api/login/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken,
                },
                credentials: 'include',
                body: JSON.stringify({ username: usernameInput, password }),
            });

            const data = await response.json();

            if (response.ok) {
                username.value = usernameInput;
                return { success: true };
            } else {
                return { success: false, error: data.error || 'Login failed' };
            }
        } catch {
            return { success: false, error: 'An error occurred' };
        }
    }

    async function logout(): Promise<void> {
        try {
            const csrfResponse = await fetch('/api/csrf-token/', {
                credentials: 'include',
            });
            const csrfData = await csrfResponse.json();
            const csrfToken = csrfData.csrfToken;

            await fetch('/api/logout/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken,
                },
                credentials: 'include',
            });
        } catch {
            // Ignore errors
        } finally {
            username.value = null;
        }
    }

    function clearUser() {
        username.value = null;
    }

    return {
        username,
        isLoading,
        isLoggedIn,
        fetchUser,
        login,
        logout,
        clearUser,
    };
});
