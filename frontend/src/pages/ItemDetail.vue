<script setup lang="ts">
import { ref, onMounted, computed, onBeforeUnmount } from "vue";
import { useRoute } from "vue-router";
import { useUserStore } from "@/stores";
import type { Question, Bid } from "../types";
import "./itemDetail.css";

type ItemDetail = {
  id: number;
  title: string;
  description?: string;
  end_time: string;
  owner_username: string;
  starting_price?: string | number | null;
  image?: string | null;
  highest_bid?: string | null;
  highest_bidder?: string | null;
  bid_count?: number;
};

const route = useRoute();
const userStore = useUserStore();
const itemId = Number(route.params.id);

const item = ref<ItemDetail | null>(null);
const bids = ref<Bid[]>([]);
const bidAmount = ref("");
const bidError = ref("");
const bidSuccess = ref("");
const bidding = ref(false);

const questions = ref<Question[]>([]);
const newQ = ref("");
const answerInputs = ref<Record<number, string>>({});
const isItemFavorited = ref(false);

const csrfToken = ref("");

const ownerUsername = ref("");

const nowTick = ref(Date.now());
let timerId: number | null = null;

function startTimer() {
  stopTimer();
  timerId = window.setInterval(() => {
    nowTick.value = Date.now();
  }, 1000);
}

function stopTimer() {
  if (timerId !== null) {
    window.clearInterval(timerId);
    timerId = null;
  }
}

const canAnswer = computed(() => {
  return (
    userStore.isLoggedIn &&
    ownerUsername.value !== "" &&
    userStore.username === ownerUsername.value
  );
});

const isOwner = computed(() => {
  return userStore.isLoggedIn && userStore.username === ownerUsername.value;
});

const isLoggedIn = computed(() => userStore.isLoggedIn);

const auctionEnded = computed(() => {
  if (!item.value) return false;
  return new Date(item.value.end_time).getTime() <= nowTick.value;
});

const currentPrice = computed(() => {
  if (!item.value) return null;
  if (item.value.highest_bid) {
    return item.value.highest_bid;
  }
  return item.value.starting_price;
});

const minimumBid = computed(() => {
  if (!item.value) return 0;
  if (item.value.highest_bid) {
    return parseFloat(item.value.highest_bid) + 0.01;
  }
  return parseFloat(String(item.value.starting_price)) || 0;
});

function formatPrice(p?: string | number | null) {
  if (p === null || p === undefined || p === "") return null;
  const n = typeof p === "string" ? Number(p) : p;
  if (Number.isNaN(n)) return String(p);
  return n.toFixed(2);
}

function formatDate(iso: string) {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return iso;

  const now = new Date();
  const sameDay =
    d.getFullYear() === now.getFullYear() &&
    d.getMonth() === now.getMonth() &&
    d.getDate() === now.getDate();

  const tomorrow = new Date(now);
  tomorrow.setDate(now.getDate() + 1);

  const isTomorrow =
    d.getFullYear() === tomorrow.getFullYear() &&
    d.getMonth() === tomorrow.getMonth() &&
    d.getDate() === tomorrow.getDate();

  const time = d.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });

  if (sameDay) return `Today, ${time}`;
  if (isTomorrow) return `Tomorrow, ${time}`;

  return d.toLocaleString(undefined, {
    day: "2-digit",
    month: "short",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function timeLeft(iso: string) {
  const end = new Date(iso).getTime();
  if (Number.isNaN(end)) return null;

  const diffMs = end - nowTick.value;
  if (diffMs <= 0) return "Ended";

  const totalSeconds = Math.floor(diffMs / 1000);

  const days = Math.floor(totalSeconds / 86400);
  const hours = Math.floor((totalSeconds % 86400) / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  if (days > 0) return `${days}d ${hours}h left`;

  const pad2 = (n: number) => String(n).padStart(2, "0");

  if (hours > 0) return `${hours}h ${pad2(minutes)}m ${pad2(seconds)}s left`;

  return `${minutes}m ${pad2(seconds)}s left`;
}

async function loadCsrf() {
  const r = await fetch("/api/csrf-token/", { credentials: "include" });
  const d: { csrfToken?: string } = await r.json();
  csrfToken.value = d.csrfToken ?? "";
}

async function loadItem() {
  const r = await fetch(`/api/items/${itemId}/`, { credentials: "include" });
  if (!r.ok) return;

  const d: ItemDetail = await r.json();
  item.value = d;
  ownerUsername.value = d.owner_username ?? "";
}

async function loadBids() {
  const r = await fetch(`/api/items/${itemId}/bids/`, { credentials: "include" });
  if (!r.ok) {
    bids.value = [];
    return;
  }
  const d: { bids?: Bid[] } = await r.json();
  bids.value = Array.isArray(d.bids) ? d.bids : [];
}

async function loadQuestions() {
  const r = await fetch(`/api/items/${itemId}/questions/`, {
    credentials: "include",
  });
  const d: { questions?: Question[] } = await r.json();
  questions.value = Array.isArray(d.questions) ? d.questions : [];
}

async function placeBid() {
  bidError.value = "";
  bidSuccess.value = "";

  const amount = parseFloat(bidAmount.value);
  if (Number.isNaN(amount) || amount <= 0) {
    bidError.value = "Please enter a valid bid amount";
    return;
  }

  bidding.value = true;

  try {
    const r = await fetch(`/api/items/${itemId}/bids/`, {
      method: "POST",
      credentials: "include",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken.value,
      },
      body: JSON.stringify({ amount }),
    });

    const d = await r.json();

    if (r.ok) {
      bidSuccess.value = "Bid placed successfully!";
      bidAmount.value = "";
      await loadItem();
      await loadBids();
    } else {
      bidError.value = d.error || "Failed to place bid";
    }
  } catch (error) {
    bidError.value = "An error occurred. Please try again.";
  } finally {
    bidding.value = false;
  }
}

async function loadItemFavorite() {
  if (!userStore.isLoggedIn) {
    isItemFavorited.value = false;
    return;
  }
  const r = await fetch(`/api/items/${itemId}/favorite/`, { credentials: "include" });
  if (!r.ok) {
    isItemFavorited.value = false;
    return;
  }
  const d: { favorited?: boolean } = await r.json();
  isItemFavorited.value = Boolean(d.favorited);
}

async function toggleItemFavorite() {
  const r = await fetch(`/api/items/${itemId}/favorite/`, {
    method: "POST",
    credentials: "include",
    headers: {
      "X-CSRFToken": csrfToken.value,
    },
  });
  if (!r.ok) {
    return;
  }
  const d: { favorited?: boolean } = await r.json();
  isItemFavorited.value = Boolean(d.favorited);
}

async function askQuestion() {
  const text = newQ.value.trim();
  if (!text) return;

  await fetch(`/api/items/${itemId}/questions/`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken.value,
    },
    body: JSON.stringify({ text }),
  });

  newQ.value = "";
  await loadQuestions();
}

async function answerQuestion(id: number) {
  const answer = (answerInputs.value[id] ?? "").trim();
  if (!answer) return;

  await fetch(`/api/questions/${id}/answer/`, {
    method: "POST",
    credentials: "include",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken.value,
    },
    body: JSON.stringify({ answer_text: answer }),
  });

  answerInputs.value[id] = "";
  await loadQuestions();
}

onMounted(async () => {
  await loadCsrf();
  await loadItem();
  await userStore.fetchUser();
  await loadItemFavorite();
  await loadBids();
  await loadQuestions();
  startTimer();
});

onBeforeUnmount(() => {
  stopTimer();
});
</script>

<template>
  <div class="detail-page" v-if="item">
    <div class="detail-grid">
      <!-- LEFT: Image -->
      <section class="detail-left">
        <div class="card">
          <div class="media-box">
            <img v-if="item.image" class="media-img" :src="item.image" alt="Item image" />
            <div v-else class="media-placeholder">📦</div>
          </div>
        </div>
      </section>

      <!-- RIGHT: Summary -->
      <aside class="detail-right">
        <div class="card summary-card">
          <div class="title-row">
            <h1 class="title">{{ item.title }}</h1>
            <button
              class="heart-btn"
              :class="{ active: isItemFavorited }"
              :disabled="!userStore.isLoggedIn"
              :title="userStore.isLoggedIn ? 'Toggle wishlist' : 'Log in to use wishlist'"
              @click="toggleItemFavorite"
            >
              <span aria-hidden="true">{{ isItemFavorited ? "♥" : "♡" }}</span>
              <span class="sr-only">Toggle wishlist</span>
            </button>
          </div>

          <div class="price-block">
            <div class="price-label">{{ item.highest_bid ? "Current Bid" : "Starting Price" }}</div>
            <div v-if="formatPrice(currentPrice) !== null" class="price">
              £{{ formatPrice(currentPrice) }}
            </div>
            <div v-else class="price muted">£—</div>

            <div v-if="item.bid_count" class="bid-count">
              {{ item.bid_count }} bid{{ item.bid_count !== 1 ? "s" : "" }}
              <span v-if="item.highest_bidder" class="highest-bidder">
                · Highest: {{ item.highest_bidder }}
              </span>
            </div>

            <div class="subline">
              <span class="left" :class="{ ended: timeLeft(item.end_time) === 'Ended' }">
                {{ timeLeft(item.end_time) ?? "" }}
              </span>
              <span class="dot">•</span>
              <span class="right">Ends: {{ formatDate(item.end_time) }}</span>
            </div>
          </div>

          <p v-if="item.description" class="desc">{{ item.description }}</p>

          <div class="meta-row">
            <span class="pill">Owner: {{ item.owner_username }}</span>
            <span v-if="userStore.username" class="pill">You: {{ userStore.username }}</span>
          </div>

          <!-- Bidding Section -->
          <div class="bid-section">
            <div v-if="auctionEnded" class="bid-ended">
              <p class="ended-text">🔒 This auction has ended</p>
              <p v-if="item.highest_bidder" class="winner-text">
                Winner: <strong>{{ item.highest_bidder }}</strong> with £{{ formatPrice(item.highest_bid) }}
              </p>
            </div>

            <div v-else-if="isOwner" class="bid-owner">
              <p class="owner-text">This is your listing. You cannot bid on your own item.</p>
            </div>

            <div v-else-if="!isLoggedIn" class="bid-login">
              <p class="login-text">Please log in to place a bid.</p>
            </div>

            <div v-else class="bid-form">
              <!-- ✅ CHANGED AREA: £ is now inside the input box -->
              <div class="bid-input-row">
                <div class="bid-input-wrap">
                  <span class="currency">£</span>
                  <input
                    v-model="bidAmount"
                    type="number"
                    step="0.01"
                    :min="minimumBid"
                    class="bid-input"
                    :placeholder="`Min: ${minimumBid.toFixed(2)}`"
                  />
                </div>

                <button class="bid-btn" @click="placeBid" :disabled="bidding">
                  {{ bidding ? "Placing..." : "Place Bid" }}
                </button>
              </div>

              <p class="bid-hint">Enter £{{ minimumBid.toFixed(2) }} or more</p>
              <div v-if="bidError" class="bid-error">{{ bidError }}</div>
              <div v-if="bidSuccess" class="bid-success">{{ bidSuccess }}</div>
            </div>
          </div>
        </div>

        <div class="card bid-history-card">
          <h3 class="section-title">Bid History</h3>
          <p v-if="bids.length === 0" class="muted">No bids yet.</p>
          <div v-else class="bid-list">
            <div v-for="bid in bids" :key="bid.id" class="bid-item">
              <span class="bid-amount">£{{ formatPrice(bid.amount) }}</span>
              <span class="bid-bidder">{{ bid.bidder_username }}</span>
              <span class="bid-time">{{ formatDate(bid.created_at) }}</span>
            </div>
          </div>
        </div>
      </aside>
    </div>

    <!-- Q&A -->
    <section class="qa">
      <div class="card">
        <h2 class="section-title">Questions</h2>

        <p v-if="questions.length === 0" class="muted">
          No questions yet. Be the first to ask.
        </p>

        <div v-else class="q-list">
          <div v-for="q in questions" :key="q.id" class="q-item">
            <div class="q-top">
              <span class="q-user">{{ q.asked_by }}</span>
              <span class="q-text">{{ q.text }}</span>
            </div>

            <div v-if="q.answer_text" class="answer">
              <span class="answer-label">Owner:</span>
              <span>{{ q.answer_text }}</span>
            </div>

            <div v-else-if="canAnswer" class="answer-box">
              <input v-model="answerInputs[q.id]" class="input" placeholder="Write answer..." />
              <button class="btn" @click="answerQuestion(q.id)">Send</button>
            </div>
          </div>
        </div>
      </div>

      <div class="card">
        <h3 class="section-title">Ask a question</h3>

        <div class="ask-row">
          <input
            v-model="newQ"
            class="input"
            placeholder="e.g. Any scratches? Is pickup possible?"
            @keydown.enter="askQuestion"
          />
          <button class="btn" @click="askQuestion">Submit</button>
        </div>

        <p class="tip muted">Tip: Keep it short and clear.</p>
      </div>
    </section>
  </div>

  <div v-else class="detail-page">
    <p class="muted">Loading item…</p>
  </div>
</template>