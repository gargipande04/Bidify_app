<template>
    <div class="landing-page">
        <div class="hero-section">
            <h1 class="hero-title">Welcome to Bidify</h1>
            <p class="hero-subtitle">Discover amazing items and place your bids</p>
            <div class="hero-buttons">
                <router-link to="/signup" class="btn btn-primary">Get Started</router-link>
                <router-link to="/login" class="btn btn-secondary">Login</router-link>
            </div>
        </div>

        <div class="features-section">
            <h2>How It Works</h2>
            <div class="features-grid">
                <div class="feature-card">
                    <h3>Create Account</h3>
                    <p>Sign up for free and create your profile</p>
                </div>
                <div class="feature-card">
                    <h3>Browse Items</h3>
                    <p>Explore a wide variety of items up for auction</p>
                </div>
                <div class="feature-card">
                    <h3>Place Bids</h3>
                    <p>Bid on items you're interested in</p>
                </div>
                <div class="feature-card">
                    <h3>Win & Purchase</h3>
                    <p>Get notified when you win an auction</p>
                </div>
            </div>
        </div>

        <div class="recommendations-section">
            <h2>Recommended for You</h2>
            <p class="recommendations-subtitle">
                Based on your interests, here are a few listings you might like.
            </p>
            <p v-if="loading" class="recommendations-loading">Loading recommendations...</p>
            <p v-else-if="recommendations.length === 0" class="recommendations-empty">
                Add interests on your profile or sign up to see tailored listings.
            </p>
            <div v-else class="recommendations-grid">
                <router-link
                    v-for="item in recommendations"
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
        </div>

        <div class="cta-section">
            <h2>Ready to Start?</h2>
            <p>Join our community of buyers and sellers today</p>
            <router-link to="/signup" class="btn btn-primary">Sign Up Now</router-link>
        </div>
    </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import type { ItemSummary } from '../../types';
import './landing.css';

const recommendations = ref<ItemSummary[]>([]);
const loading = ref(false);

const loadRecommendations = async (): Promise<void> => {
    loading.value = true;
    try {
        const response = await fetch('/api/recommendations/', { method: 'GET', credentials: 'include' });
        if (!response.ok) {
            recommendations.value = [];
            return;
        }
        const data = await response.json();
        recommendations.value = Array.isArray(data.items) ? data.items : [];
    } catch (error) {
        console.error('Recommendation load error:', error);
    } finally {
        loading.value = false;
    }
};

onMounted(loadRecommendations);
</script>
