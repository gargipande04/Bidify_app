<template>
    <div class="profile-page">
        <div class="profile-card">
            <div class="profile-header">
                <div>
                    <h1>Profile</h1>
                    <p class="profile-subtitle">Manage your account details and keep your profile up to date.</p>
                </div>
            </div>

            <div class="profile-grid">
                <section class="profile-panel profile-view">
                    <div class="panel-header">
                        <h2>{{ form.email || 'Profile' }}</h2>
                    </div>
                    <div class="overview-avatar">
                        <img
                            v-if="previewUrl"
                            :src="previewUrl"
                            alt="Profile image"
                        />
                        <div v-else class="avatar-placeholder">No image</div>
                    </div>
                    <div class="overview-details">
                        <p><span>Date of birth</span> {{ form.date_of_birth || 'Not set' }}</p>
                    </div>
                    <div class="interest-bubbles">
                        <p class="interest-title">Interests</p>
                        <div v-if="interests.length === 0" class="muted">No interests selected.</div>
                        <div v-else class="bubble-row">
                            <span v-for="interest in interests" :key="interest.id" class="bubble">
                                {{ interest.name }}
                            </span>
                        </div>
                    </div>
                </section>

                <section class="profile-panel profile-edit">
                    <div class="panel-header">
                        <h2>Update profile</h2>
                    </div>
                    <form class="profile-form" @submit.prevent="handleSave">
                        <div class="form-group">
                            <label for="email">Email</label>
                            <input
                                id="email"
                                v-model="form.email"
                                type="email"
                                placeholder="you@example.com"
                                required
                            />
                        </div>

                        <div class="form-group">
                            <label for="dob">Date of birth</label>
                            <input id="dob" v-model="form.date_of_birth" type="date" />
                        </div>

                        <div class="form-group">
                            <label for="profile-picture">Profile image</label>
                            <input id="profile-picture" type="file" accept="image/*" @change="handleFileChange" />
                        </div>

                        <div v-if="previewUrl" class="image-preview">
                            <img :src="previewUrl" alt="Profile preview" />
                        </div>

                        <p v-if="errorMessage" class="form-error">{{ errorMessage }}</p>
                        <p v-if="successMessage" class="form-success">{{ successMessage }}</p>

                        <button type="submit" :disabled="saving">
                            {{ saving ? 'Saving...' : 'Save changes' }}
                        </button>
                    </form>
                </section>
            </div>

            <section class="profile-panel profile-wishlist">
                <div class="panel-header">
                    <h2>Wishlist</h2>
                    <p>Saved items you want to revisit.</p>
                </div>
                <p v-if="wishlistError" class="form-error">{{ wishlistError }}</p>
                <p v-else-if="wishlist.length === 0" class="muted">No favourites yet.</p>
                <div v-else class="wishlist-list">
                    <div v-for="entry in wishlist" :key="entry.id" class="wishlist-row">
                        <div class="wishlist-info">
                            <p class="wishlist-title">{{ entry.title }}</p>
                            <p class="wishlist-meta">
                                £{{ Number(entry.starting_price).toFixed(2) }} ·
                                {{ formatDate(entry.end_time) }}
                            </p>
                        </div>
                        <button class="btn ghost" type="button" @click="removeFavorite(entry.id)">
                            Remove
                        </button>
                    </div>
                </div>
            </section>

            <section class="profile-panel profile-activity">
                <div class="panel-header">
                    <h2>Your activity</h2>
                    <p>Track listings you've created and bids you've placed.</p>
                </div>
                <p v-if="activityError" class="form-error">{{ activityError }}</p>
                <div v-else class="activity-grid">
                    <div class="activity-column">
                        <h3>Listings</h3>
                        <div class="activity-group">
                            <h4>Current</h4>
                            <p v-if="myItems.current.length === 0" class="muted">No active listings.</p>
                            <div v-else class="activity-list">
                                <div v-for="item in myItems.current" :key="item.id" class="activity-row">
                                    <div>
                                        <p class="activity-title">{{ item.title }}</p>
                                        <p class="activity-meta">
                                            Ends {{ formatDate(item.end_time) }} · £{{ Number(item.starting_price).toFixed(2) }}
                                        </p>
                                    </div>
                                    <button class="btn ghost" type="button" @click="deleteListing(item.id)">
                                        Delete
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div class="activity-group">
                            <h4>Past</h4>
                            <p v-if="myItems.past.length === 0" class="muted">No past listings.</p>
                            <div v-else class="activity-list">
                                <div v-for="item in myItems.past" :key="item.id" class="activity-row">
                                    <div>
                                        <p class="activity-title">{{ item.title }}</p>
                                        <p class="activity-meta">
                                            Ended {{ formatDate(item.end_time) }} · £{{ Number(item.starting_price).toFixed(2) }}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                    <div class="activity-column">
                        <h3>Bids</h3>
                        <div class="activity-group">
                            <h4>Current</h4>
                            <p v-if="myBids.current.length === 0" class="muted">No active bids.</p>
                            <div v-else class="activity-list">
                                <div v-for="bid in myBids.current" :key="bid.id" class="activity-row">
                                    <div>
                                        <p class="activity-title">{{ bid.item.title }}</p>
                                        <p class="activity-meta">
                                            Bid £{{ Number(bid.amount).toFixed(2) }} ·
                                            Ends {{ formatDate(bid.item.end_time) }}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="activity-group">
                            <h4>Past</h4>
                            <p v-if="myBids.past.length === 0" class="muted">No past bids.</p>
                            <div v-else class="activity-list">
                                <div v-for="bid in myBids.past" :key="bid.id" class="activity-row">
                                    <div>
                                        <p class="activity-title">{{ bid.item.title }}</p>
                                        <p class="activity-meta">
                                            Bid £{{ Number(bid.amount).toFixed(2) }} ·
                                            Ended {{ formatDate(bid.item.end_time) }}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </section>
        </div>
    </div>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from 'vue';
import type { FavoriteItemResponse, ItemSummary, UserBid } from '../../types';
import './profile.css';

const API_BASE = '';

const form = reactive({
    email: '',
    date_of_birth: '',
});
const interests = ref<Array<{ id: number; name: string; parent_name: string | null }>>([]);

const selectedFile = ref<File | null>(null);
const previewUrl = ref<string | null>(null);
const errorMessage = ref<string>('');
const successMessage = ref<string>('');
const saving = ref<boolean>(false);
const wishlist = ref<ItemSummary[]>([]);
const wishlistError = ref<string>('');
const myItems = ref<{ current: ItemSummary[]; past: ItemSummary[] }>({ current: [], past: [] });
const myBids = ref<{ current: UserBid[]; past: UserBid[] }>({ current: [], past: [] });
const activityError = ref<string>('');

const normalizeImageUrl = (url: string | null): string | null => {
    if (!url) return null;
    if (url.startsWith('http')) return url;
    return `${API_BASE}/${url.replace(/^\//, '')}`;
};


const formatDate = (iso: string): string => {
    const d = new Date(iso);
    if (Number.isNaN(d.getTime())) return iso;
    return d.toLocaleString(undefined, {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
    });
};

const getCsrfToken = async (): Promise<string> => {
    const csrfResponse = await fetch(`${API_BASE}/api/csrf-token/`, {
        method: 'GET',
        credentials: 'include',
    });
    const csrfData = await csrfResponse.json();
    return csrfData.csrfToken || '';
};

const loadProfile = async (): Promise<void> => {
    errorMessage.value = '';
    try {
        const response = await fetch(`${API_BASE}/api/profile/`, {
            method: 'GET',
            credentials: 'include',
        });
        if (!response.ok) {
            throw new Error('Failed to load profile.');
        }
        const data = await response.json();
        form.email = data.email || '';
        form.date_of_birth = data.date_of_birth || '';
        previewUrl.value = normalizeImageUrl(data.profile_picture || null);
        interests.value = Array.isArray(data.interests_detail) ? data.interests_detail : [];
    } catch (error) {
        errorMessage.value = 'Unable to load profile. Please log in again.';
        console.error('Profile load error:', error);
    }
};

const loadWishlist = async (): Promise<void> => {
    wishlistError.value = '';
    try {
        const response = await fetch(`${API_BASE}/api/wishlist/items/`, {
            method: 'GET',
            credentials: 'include',
        });
        if (!response.ok) {
            throw new Error('Failed to load wishlist.');
        }
        const data: FavoriteItemResponse = await response.json();
        wishlist.value = Array.isArray(data.items) ? data.items : [];
    } catch (error) {
        wishlistError.value = 'Unable to load wishlist.';
        console.error('Wishlist load error:', error);
    }
};

const loadActivity = async (): Promise<void> => {
    activityError.value = '';
    try {
        const [itemsRes, bidsRes] = await Promise.all([
            fetch(`${API_BASE}/api/profile/items/`, { method: 'GET', credentials: 'include' }),
            fetch(`${API_BASE}/api/profile/bids/`, { method: 'GET', credentials: 'include' }),
        ]);
        if (!itemsRes.ok || !bidsRes.ok) {
            throw new Error('Failed to load activity.');
        }
        const itemsData = await itemsRes.json();
        const bidsData = await bidsRes.json();
        myItems.value = {
            current: Array.isArray(itemsData.current) ? itemsData.current : [],
            past: Array.isArray(itemsData.past) ? itemsData.past : [],
        };
        myBids.value = {
            current: Array.isArray(bidsData.current) ? bidsData.current : [],
            past: Array.isArray(bidsData.past) ? bidsData.past : [],
        };
    } catch (error) {
        activityError.value = 'Unable to load your activity right now.';
        console.error('Activity load error:', error);
    }
};

const removeFavorite = async (itemId: number): Promise<void> => {
    try {
        const csrfToken = await getCsrfToken();
        const response = await fetch(`${API_BASE}/api/items/${itemId}/favorite/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            },
            credentials: 'include',
        });
        if (!response.ok) {
            throw new Error('Failed to update wishlist.');
        }
        wishlist.value = wishlist.value.filter((entry) => entry.id !== itemId);
    } catch (error) {
        wishlistError.value = 'Unable to update wishlist.';
        console.error('Wishlist update error:', error);
    }
};

const deleteListing = async (itemId: number): Promise<void> => {
    try {
        const csrfToken = await getCsrfToken();
        const response = await fetch(`${API_BASE}/api/items/${itemId}/delete/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken,
            },
            credentials: 'include',
        });
        if (!response.ok) {
            throw new Error('Failed to delete listing.');
        }
        myItems.value.current = myItems.value.current.filter((item) => item.id !== itemId);
    } catch (error) {
        activityError.value = 'Unable to delete listing.';
        console.error('Delete listing error:', error);
    }
};

const handleFileChange = (event: Event): void => {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0] || null;
    selectedFile.value = file;
    if (file) {
        previewUrl.value = URL.createObjectURL(file);
    }
};

const handleSave = async (): Promise<void> => {
    errorMessage.value = '';
    successMessage.value = '';
    saving.value = true;
    try {
        const csrfToken = await getCsrfToken();

        const payload = new FormData();
        payload.append('email', form.email);
        if (form.date_of_birth) {
            payload.append('date_of_birth', form.date_of_birth);
        }
        if (selectedFile.value) {
            payload.append('profile_picture', selectedFile.value);
        }

        const response = await fetch(`${API_BASE}/api/profile/`, {
            method: 'PATCH',
            headers: {
                'X-CSRFToken': csrfToken,
            },
            credentials: 'include',
            body: payload,
        });

        const data = await response.json();
        if (!response.ok) {
            errorMessage.value = data.error || 'Failed to update profile.';
            return;
        }

        form.email = data.email || '';
        form.date_of_birth = data.date_of_birth || '';
        previewUrl.value = normalizeImageUrl(data.profile_picture || null);
        selectedFile.value = null;
        successMessage.value = 'Profile updated.';
    } catch (error) {
        errorMessage.value = 'Something went wrong. Please try again.';
        console.error('Profile save error:', error);
    } finally {
        saving.value = false;
    }
};

onMounted(async () => {
    await loadProfile();
    await loadWishlist();
    await loadActivity();
});
</script>
