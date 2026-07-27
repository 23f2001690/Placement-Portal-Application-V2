import { apiFetch, logout } from "/src/api.js";

export default {
    data() {
        return { loading: true };
    },
    async mounted() {
        try {
            await apiFetch("/api/auth/me");
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
            <h3>Admin Dashboard</h3>
            <button class="btn btn-outline-danger btn-sm" @click="logout">Logout</button>
          </div>
          <p v-if="loading">Loading...</p>
          <p v-else class="text-muted">Logged in as Admin. Widgets for companies, students and drives come next.</p>
        </div>
    `,
};