import { apiFetch, logout } from "/src/api.js";

export default {
    data() {
        return { loading: true, profile: null };
    },
    async mounted() {
        try {
            const data = await apiFetch("/api/auth/me");
            this.profile = data.profile;
        } catch (e) {
            window.location.hash = "/login";
        } finally {
            this.loading = false;
        }
    },
    methods: { logout },
    template: `
        <div class="container py-4">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h3>Student Dashboard</h3>
            <button class="btn btn-outline-danger btn-sm" @click="logout">Logout</button>
          </div>
          <div v-if="loading">Loading...</div>
          <div v-else-if="profile">
            <p>Welcome, <strong>{{ profile.name }}</strong></p>
            <p class="text-muted">Placement drives and applications come next.</p>
          </div>
        </div>
    `,
};