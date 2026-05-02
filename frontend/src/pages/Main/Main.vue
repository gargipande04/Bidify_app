<template>
    <div class="main-page">
        <header class="main-hero">
            <h1>Welcome back</h1>
            <p>Here are listings matched to your interests.</p>
        </header>

        <section class="recommendations">
            <h2>Recommended for you</h2>
            <p v-if="loading" class="muted">Loading recommendations...</p>
            <p v-else-if="items.length === 0" class="muted">
                You may like...
            </p>
            <div v-else class="recommendations-grid">
                <router-link
                    v-for="item in items"
                    :key="item.id"
                    :to="{ name: 'ItemDetail', params: { id: item.id } }"
                    class="recommendation-card"
                >
                    <div class="recommendation-thumb">
                        <img v-if="item.image" :src="item.image" alt="Item image" />
                        <div v-else class="recommendation-placeholder">✨</div>
                    </div>
                    <div class="recommendation-body">
                        <h3>{{ item.title }}</h3>
                        <p>£{{ Number(item.starting_price).toFixed(2) }}</p>
                        <span v-if="item.category_name" class="recommendation-tag">
                            {{ item.category_parent ? item.category_parent + ' / ' : '' }}{{ item.category_name }}
                        </span>
                    </div>
                </router-link>
            </div>
        </section>
    </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import type { ItemSummary } from '../../types';
import './main.css';

const items = ref<ItemSummary[]>([]);
const loading = ref(false);

const loadRecommendations = async (): Promise<void> => {
    loading.value = true;
    try {
        const response = await fetch('/api/recommendations/', {
            method: 'GET',
            credentials: 'include',
        });
        if (!response.ok) {
            items.value = [];
            return;
        }
        const data = await response.json();
        items.value = Array.isArray(data.items) ? data.items : [];
    } catch (error) {
        console.error('Recommendation load error:', error);
    } finally {
        loading.value = false;
    }
};

onMounted(loadRecommendations);
</script>
