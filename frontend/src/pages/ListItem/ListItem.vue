<template>
    <div class="list-item-page">
        <div class="list-item-card">
            <h1 class="page-title">List an Item for Auction</h1>
            <p class="page-subtitle">Fill in the details below to create your auction listing</p>
            
            <form @submit.prevent="handleSubmit" class="list-item-form">
                <div class="form-group">
                    <label for="title">Title *</label>
                    <input
                        id="title"
                        v-model="formData.title"
                        type="text"
                        class="form-control"
                        placeholder="Enter item title"
                        required
                    />
                </div>

                <div class="form-group">
                    <label for="description">Description *</label>
                    <textarea
                        id="description"
                        v-model="formData.description"
                        class="form-control textarea"
                        placeholder="Describe your item in detail"
                        rows="4"
                        required
                    ></textarea>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="starting_price">Starting Price (£) *</label>
                        <input
                            id="starting_price"
                            v-model="formData.starting_price"
                            type="number"
                            step="0.01"
                            min="0"
                            class="form-control"
                            placeholder="0.00"
                            required
                        />
                    </div>
                    <div class="form-group">
                        <label for="end_time">Auction End Date & Time *</label>
                        <input
                            id="end_time"
                            v-model="formData.end_time"
                            type="datetime-local"
                            class="form-control"
                            :min="minDateTime"
                            required
                        />
                    </div>
                </div>

                <div class="form-row">
                    <div class="form-group">
                        <label for="category-parent">Category *</label>
                        <select
                            id="category-parent"
                            v-model="selectedParentId"
                            class="form-control"
                            required
                        >
                            <option value="">Select a category</option>
                            <option v-for="group in categories" :key="group.id" :value="group.id">
                                {{ group.name }}
                            </option>
                        </select>
                    </div>
                    <div class="form-group">
                        <label for="category-child">Subcategory *</label>
                        <select
                            id="category-child"
                            v-model="formData.category_id"
                            class="form-control"
                            :disabled="!selectedParentId"
                            required
                        >
                            <option value="">Select a subcategory</option>
                            <option
                                v-for="child in selectedChildren"
                                :key="child.id"
                                :value="child.id"
                            >
                                {{ child.name }}
                            </option>
                        </select>
                    </div>
                </div>

                <div class="form-group">
                    <label>Item Image</label>
                    <div class="image-upload-area" @click="triggerFileInput" @dragover.prevent @drop.prevent="handleDrop">
                        <input
                            ref="fileInput"
                            type="file"
                            accept="image/*"
                            @change="handleImageSelect"
                            hidden
                        />
                        <div v-if="imagePreview" class="image-preview">
                            <img :src="imagePreview" alt="Preview" />
                            <button type="button" class="remove-image" @click.stop="removeImage">×</button>
                        </div>
                        <div v-else class="upload-placeholder">
                            <span class="upload-icon">📷</span>
                            <span class="upload-text">Click or drag to upload an image</span>
                        </div>
                    </div>
                </div>

                <div v-if="errorMessage" class="alert alert-danger">
                    {{ errorMessage }}
                </div>
                
                <div v-if="successMessage" class="alert alert-success">
                    {{ successMessage }}
                </div>

                <button type="submit" class="btn btn-primary" :disabled="submitting">
                    <span v-if="submitting">Creating Listing...</span>
                    <span v-else>Create Listing</span>
                </button>
            </form>
        </div>
    </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import type { CategoryGroup } from '../../types';
import './listitem.css';

interface ItemFormData {
    title: string;
    description: string;
    starting_price: string;
    end_time: string;
    category_id: number | '';
}

const formData = reactive<ItemFormData>({
    title: '',
    description: '',
    starting_price: '',
    end_time: '',
    category_id: '',
});

const categories = ref<CategoryGroup[]>([]);
const selectedParentId = ref<string>('');

const selectedChildren = computed(() => {
    const parentId = Number(selectedParentId.value);
    const group = categories.value.find((item) => item.id === parentId);
    return group ? group.children : [];
});

const fileInput = ref<HTMLInputElement | null>(null);
const selectedImage = ref<File | null>(null);
const imagePreview = ref<string | null>(null);
const submitting = ref(false);
const errorMessage = ref('');
const successMessage = ref('');

const minDateTime = computed(() => {
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    return now.toISOString().slice(0, 16);
});

const triggerFileInput = () => {
    fileInput.value?.click();
};

const handleImageSelect = (event: Event) => {
    const target = event.target as HTMLInputElement;
    const file = target.files?.[0];
    if (file) {
        selectedImage.value = file;
        imagePreview.value = URL.createObjectURL(file);
    }
};

const handleDrop = (event: DragEvent) => {
    const file = event.dataTransfer?.files?.[0];
    if (file && file.type.startsWith('image/')) {
        selectedImage.value = file;
        imagePreview.value = URL.createObjectURL(file);
    }
};

const removeImage = () => {
    selectedImage.value = null;
    imagePreview.value = null;
    if (fileInput.value) {
        fileInput.value.value = '';
    }
};

const resetForm = () => {
    formData.title = '';
    formData.description = '';
    formData.starting_price = '';
    formData.end_time = '';
    formData.category_id = '';
    selectedParentId.value = '';
    removeImage();
};

const handleSubmit = async () => {
    errorMessage.value = '';
    successMessage.value = '';
    submitting.value = true;

    if (!formData.category_id) {
        errorMessage.value = 'Please choose a category and subcategory.';
        submitting.value = false;
        return;
    }

    try {
        // Get CSRF token
        const csrfResponse = await fetch('/api/csrf-token/', {
            method: 'GET',
            credentials: 'include',
        });
        const csrfData = await csrfResponse.json();
        const csrfToken = csrfData.csrfToken;

        // Create FormData for multipart upload
        const submitData = new FormData();
        submitData.append('title', formData.title);
        submitData.append('description', formData.description);
        submitData.append('starting_price', formData.starting_price);
        submitData.append('end_time', formData.end_time);
        submitData.append('category_id', String(formData.category_id));
        
        if (selectedImage.value) {
            submitData.append('image', selectedImage.value);
        }

        const response = await fetch('/api/items/create/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
            },
            credentials: 'include',
            body: submitData,
        });

        const data = await response.json();

        if (response.ok) {
            successMessage.value = 'Item listed successfully!';
            resetForm();
        } else {
            errorMessage.value = data.error || 'Failed to create listing';
        }
    } catch (error) {
        errorMessage.value = 'An error occurred. Please try again.';
        console.error('Create listing error:', error);
    } finally {
        submitting.value = false;
    }
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

loadCategories();
</script>
