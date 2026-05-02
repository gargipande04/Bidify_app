<template>
  <div class="items-page">
    <header class="items-header">
      <h1 class="items-title">Items</h1>

      <div class="search-row">
        <input
          v-model="query"
          class="items-search-input"
          type="text"
          placeholder="Search items..."
          @keydown.enter="onEnterSearch"
        />
        <button class="items-search-btn" @click="runSearchNow" :disabled="loading">
          Search
        </button>
      </div>

      <div class="tools-row">
        <div class="tool">
          <label class="tool-label" for="sort">Sort</label>
          <select id="sort" v-model="sortKey" class="tool-select">
            <option value="default">Default</option>
            <option value="ending">Ending soon</option>
            <option value="price_asc">Price: low → high</option>
            <option value="price_desc">Price: high → low</option>
            <option value="title_asc">Title: A → Z</option>
            <option value="title_desc">Title: Z → A</option>
          </select>
        </div>

        <div class="tool">
          <label class="tool-label" for="minPrice">Min £</label>
          <input
            id="minPrice"
            v-model.number="minPrice"
            class="tool-input"
            type="number"
            inputmode="decimal"
            placeholder="0"
            min="0"
          />
        </div>

        <div class="tool">
          <label class="tool-label" for="maxPrice">Max £</label>
          <input
            id="maxPrice"
            v-model.number="maxPrice"
            class="tool-input"
            type="number"
            inputmode="decimal"
            placeholder="1000"
            min="0"
          />
        </div>

        <div class="tool">
          <label class="tool-label" for="hasImage">Has image</label>
          <label class="has-image-wrap has-image-wrap--wide" for="hasImage">
            <input id="hasImage" type="checkbox" v-model="hasImage" />
            <span class="has-image-label">items with images</span>
          </label>
        </div>

        <div class="tool">
          <label class="tool-label" for="clearAllBtn">Reset</label>
          <button
            id="clearAllBtn"
            class="has-image-wrap clear-all-box"
            type="button"
            @click="clearAll"
            :disabled="loading"
          >
            Clear all
          </button>
        </div>
      </div>

      <p class="results-summary" v-if="!loading && !error">
        Showing {{ pagedItems.length }} of {{ displayItems.length }} items
      </p>
    </header>

    <section v-if="filteredCategories.length" class="category-section">
      <h2 class="category-title">Browse by category</h2>
      <div class="category-grid">
        <div
          v-for="group in orderedCategories"
          :key="group.id"
          class="category-card"
          :class="{ 'category-card--all': group.name.toLowerCase() === 'all' }"
          :style="{ '--card-bg': categoryBackground(group.name) }"
        >
          <button
            class="category-flip"
            type="button"
            @click="toggleCategory(group.id)"
            :aria-pressed="openParentId === group.id"
          >
            <div class="flip-inner" :class="{ flipped: openParentId === group.id }">
              <div class="flip-front">
                <h3>{{ group.name }}</h3>
                <p>Tap to see subcategories</p>
              </div>
              <div class="flip-back">
                <h3>{{ group.name }}</h3>
                <div class="category-tags">
                  <button
                    v-for="child in visibleChildren(group)"
                    :key="child.id"
                    class="category-tag"
                    :class="{ active: activeCategoryId === child.id }"
                    type="button"
                    @click.stop="handleCategorySelect(child.id)"
                  >
                    {{ child.name }}
                  </button>
                </div>
              </div>
            </div>
          </button>
        </div>
      </div>

      <button
        v-if="activeCategoryId !== null"
        type="button"
        class="clear-category-btn"
        @click="clearCategoryFilter"
      >
        Clear category filter
      </button>
    </section>

    <!-- Skeleton Loading -->
    <div v-if="loading" class="skeleton-grid" aria-busy="true" aria-label="Loading items">
      <div v-for="n in 9" :key="n" class="skeleton-card">
        <div class="skeleton-thumb"></div>
        <div class="skeleton-lines">
          <div class="skeleton-line w-70"></div>
          <div class="skeleton-line w-40"></div>
          <div class="skeleton-line w-90"></div>
        </div>
      </div>
    </div>

    <p v-else-if="error" class="items-error">{{ error }}</p>

    <p v-else-if="displayItems.length === 0" class="items-empty">
      No items found<span v-if="query.trim()"> for “{{ query.trim() }}”</span>.
    </p>

    <template v-else>
      <!-- Items grid -->
      <ul class="items-grid">
        <li v-for="item in pagedItems" :key="item.id" class="item-card">
          <router-link class="item-link" :to="`/main/items/${item.id}`">
            <div class="thumb">
              <img v-if="item.image" :src="item.image" alt="Item image" class="thumb-img" />
              <div v-else class="thumb-placeholder">
                <span>📦</span>
              </div>
            </div>

            <div class="item-body">
              <div class="top-row">
                <h2 class="item-title">{{ item.title }}</h2>

                <div
                  v-if="item.starting_price !== null && item.starting_price !== undefined"
                  class="price"
                >
                  £{{ formatPrice(item.starting_price) }}
                </div>
              </div>

              <p v-if="item.description" class="desc">
                {{ truncate(item.description, 90) }}
              </p>

              <div class="meta-row">
                <span class="pill">Owner: {{ item.owner_username }}</span>

                <span v-if="item.category_name" class="pill">
                  {{ item.category_parent ? item.category_parent + " / " : "" }}{{ item.category_name }}
                </span>

                <span class="pill">Ends: {{ formatDate(item.end_time) }}</span>
              </div>
            </div>
          </router-link>
        </li>
      </ul>

      <div v-if="canLoadMore" class="load-more-row">
        <button class="load-more-btn" type="button" @click="loadMore">
          Load more
        </button>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import type { CategoryGroup, ItemSummary } from "../../types";
import "./items.css";
import kidsImg from "@/assets/image_1.png";
import allImg from "@/assets/image_2.png";
import womenImg from "@/assets/image_3.png";
import menImg from "@/assets/image_4.png";

const items = ref<ItemSummary[]>([]);
const originalItems = ref<ItemSummary[]>([]);
const categories = ref<CategoryGroup[]>([]);

const query = ref<string>("");
const loading = ref(false);
const error = ref<string>("");

const activeCategoryId = ref<number | null>(null);
const openParentId = ref<number | null>(null);

const sortKey = ref<
  "default" | "ending" | "price_asc" | "price_desc" | "title_asc" | "title_desc"
>("default");

const hasImage = ref(false);
const minPrice = ref<number | null>(null);
const maxPrice = ref<number | null>(null);

/* Pagination */
const PAGE_SIZE = 12;
const visibleCount = ref(PAGE_SIZE);

function loadMore() {
  visibleCount.value += PAGE_SIZE;
}

const filteredCategories = computed(() => {
  return categories.value.filter((group) => {
    const name = group.name.toLowerCase();
    return name !== "everything else" && name !== "other";
  });
});

function truncate(text: string, maxLen: number) {
  const t = text.trim();
  if (t.length <= maxLen) return t;
  return t.slice(0, maxLen).trimEnd() + "…";
}

function formatDate(iso: string) {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;
  return d.toLocaleString(undefined, {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function formatPrice(p: string | number) {
  const n = typeof p === "string" ? Number(p) : p;
  if (Number.isNaN(n)) return String(p);
  return n.toFixed(2);
}

function priceNumber(p: unknown): number | null {
  if (p === null || p === undefined) return null;
  const n = typeof p === "string" ? Number(p) : typeof p === "number" ? p : Number(p);
  return Number.isFinite(n) ? n : null;
}

function dateNumber(iso: string): number {
  const t = new Date(iso).getTime();
  return Number.isFinite(t) ? t : 0;
}

function itemPrice(i: any): number | null {
  return priceNumber(i.highest_bid ?? i.starting_price);
}

const displayItems = computed(() => {
  let list = [...originalItems.value];

  if (hasImage.value) {
    list = list.filter((i: any) => Boolean(i.image));
  }

  let min =
    typeof minPrice.value === "number" && Number.isFinite(minPrice.value) ? minPrice.value : null;
  let max =
    typeof maxPrice.value === "number" && Number.isFinite(maxPrice.value) ? maxPrice.value : null;

  if (min !== null && max !== null && min > max) {
    [min, max] = [max, min];
  }

  if (min !== null) {
    list = list.filter((i: any) => {
      const p = itemPrice(i);
      return p !== null && p >= min!;
    });
  }

  if (max !== null) {
    list = list.filter((i: any) => {
      const p = itemPrice(i);
      return p !== null && p <= max!;
    });
  }

  switch (sortKey.value) {
    case "default":
      break;
    case "ending":
      list.sort((a: any, b: any) => dateNumber(a.end_time) - dateNumber(b.end_time));
      break;
    case "price_asc":
      list.sort(
        (a: any, b: any) =>
          (itemPrice(a) ?? Number.POSITIVE_INFINITY) - (itemPrice(b) ?? Number.POSITIVE_INFINITY)
      );
      break;
    case "price_desc":
      list.sort(
        (a: any, b: any) =>
          (itemPrice(b) ?? Number.NEGATIVE_INFINITY) - (itemPrice(a) ?? Number.NEGATIVE_INFINITY)
      );
      break;
    case "title_asc":
      list.sort((a: any, b: any) => String(a.title).localeCompare(String(b.title)));
      break;
    case "title_desc":
      list.sort((a: any, b: any) => String(b.title).localeCompare(String(a.title)));
      break;
  }

  return list;
});

const pagedItems = computed(() => displayItems.value.slice(0, visibleCount.value));
const canLoadMore = computed(() => displayItems.value.length > visibleCount.value);

async function loadItems() {
  loading.value = true;
  error.value = "";

  try {
    const q = query.value.trim();
    const params = new URLSearchParams();
    if (q) params.set("q", q);
    if (activeCategoryId.value !== null) params.set("category_id", String(activeCategoryId.value));

    const url = params.toString() ? `/api/items/?${params.toString()}` : "/api/items/";
    const res = await fetch(url);

    if (!res.ok) throw new Error(`Request failed: ${res.status}`);

    const data: { items: ItemSummary[] } = await res.json();
    originalItems.value = data.items ?? [];
    items.value = data.items ?? [];

    visibleCount.value = PAGE_SIZE;
  } catch (e) {
    error.value = e instanceof Error ? e.message : "Unknown error";
  } finally {
    loading.value = false;
  }
}

/* ---------------- Debounced search ---------------- */
const DEBOUNCE_MS = 400;
let searchTimer: number | undefined;

function scheduleSearch() {
  visibleCount.value = PAGE_SIZE;

  if (searchTimer) window.clearTimeout(searchTimer);
  searchTimer = window.setTimeout(() => {
    loadItems();
  }, DEBOUNCE_MS);
}

function runSearchNow() {
  if (searchTimer) window.clearTimeout(searchTimer);
  loadItems();
}

function onEnterSearch() {
  if (searchTimer) window.clearTimeout(searchTimer);
  loadItems();
}

onBeforeUnmount(() => {
  if (searchTimer) window.clearTimeout(searchTimer);
});

watch(query, () => {
  scheduleSearch();
});

function handleCategorySelect(categoryId: number) {
  activeCategoryId.value = categoryId;
  loadItems();
}

function clearCategoryFilter() {
  activeCategoryId.value = null;
  loadItems();
}

function toggleCategory(parentId: number) {
  openParentId.value = openParentId.value === parentId ? null : parentId;
}

function categoryBackground(name: string) {
  const key = name.toLowerCase();
  const backgrounds: Record<string, string> = {
    kids: kidsImg,
    all: allImg,
    women: womenImg,
    men: menImg,
  };
  const src = backgrounds[key] ?? allImg;
  return `url('${src}')`;
}

const orderedCategories = computed(() => {
  const order = ["kids", "all", "women", "men"];
  const mapped = new Map(filteredCategories.value.map((g) => [g.name.toLowerCase(), g]));
  const ordered = order.map((k) => mapped.get(k)).filter(Boolean) as CategoryGroup[];
  const remaining = filteredCategories.value.filter((g) => !order.includes(g.name.toLowerCase()));
  return [...ordered, ...remaining];
});

function visibleChildren(group: CategoryGroup) {
  return group.children;
}

async function loadCategories() {
  try {
    const res = await fetch("/api/categories/");
    if (!res.ok) return;
    const data: { categories?: CategoryGroup[] } = await res.json();
    categories.value = Array.isArray(data.categories) ? data.categories : [];
  } catch (e) {
    console.error("Category load error:", e);
  }
}

onMounted(() => {
  loadItems();
  loadCategories();
});

watch([sortKey, hasImage, minPrice, maxPrice, activeCategoryId], () => {
  visibleCount.value = PAGE_SIZE;
});

function clearAll() {
  query.value = "";
  sortKey.value = "default";
  hasImage.value = false;
  minPrice.value = null;
  maxPrice.value = null;
  activeCategoryId.value = null;
  openParentId.value = null;
  visibleCount.value = PAGE_SIZE;

  if (searchTimer) window.clearTimeout(searchTimer);
  loadItems();
}
</script>