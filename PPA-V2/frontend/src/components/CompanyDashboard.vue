import { apiFetch, logout } from "/src/api.js";

export default {
    data() {
        return { loading: true, profile: null };
    },
    computed: {
        statusBadge() {
            const map = { approved: "bg-success", pending: "bg-warning text-dark", rejected: "bg-danger" };
            return map[this.profile?.approval_status] || "bg-secondary";
        },
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
            <h3>Company Dashboard</h3>
            <button class="btn btn-outline-danger btn-sm" @click="logout">Logout</button>
          </div>
          <div v-if="loading">Loading...</div>
          <div v-else-if="profile">
            <p><strong>{{ profile.name }}</strong></p>
            <span class="badge" :class="statusBadge">{{ profile.approval_status }}</span>
            <p class="text-muted mt-3">Drive creation and applicant management come next.</p>
          </div>
        </div>
    `,
};