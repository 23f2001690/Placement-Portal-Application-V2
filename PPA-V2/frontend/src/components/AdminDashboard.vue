import { apiFetch, logout } from "/src/api.js";
import AdminCompanies from "/src/components/AdminCompanies.vue";
import AdminStudents from "/src/components/AdminStudents.vue";
import AdminJobPositions from "/src/components/AdminJobPositions.vue";
import AdminApplications from "/src/components/AdminApplications.vue";

export default {
    components: { AdminCompanies, AdminStudents, AdminJobPositions, AdminApplications },
    data() {
        return { loading: true, stats: null, activeTab: "companies", sendingReport: false, reportMessage: "" };
    },
    async mounted() {
        try {
            this.stats = await apiFetch("/api/admin/stats");
        } catch (e) {
            window.location.hash = "/login";
        } finally {
            this.loading = false;
        }
    },
    methods: {
        logout,
        async sendReport() {
            this.sendingReport = true;
            this.reportMessage = "Generating report...";
            try {
                const { task_id } = await apiFetch("/api/admin/reports/send", { method: "POST" });
                this.pollReport(task_id);
            } catch (err) {
                this.reportMessage = "Could not start report.";
                this.sendingReport = false;
            }
        },
        async pollReport(taskId) {
            const status = await apiFetch(`/api/admin/reports/status/${taskId}`);
            if (status.state === "SUCCESS") {
                this.reportMessage = "Report sent to your email.";
                this.sendingReport = false;
            } else if (status.state === "FAILURE") {
                this.reportMessage = "Report failed to send.";
                this.sendingReport = false;
            } else {
                setTimeout(() => this.pollReport(taskId), 1500);
            }
        },
    },
    template: `
        <div class="container py-4">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h3>Admin Dashboard</h3>
            <div class="d-flex align-items-center gap-2">
              <span v-if="reportMessage" class="text-muted small">{{ reportMessage }}</span>
              <button class="btn btn-outline-secondary btn-sm" :disabled="sendingReport" @click="sendReport">
                {{ sendingReport ? "Sending..." : "Email Monthly Report" }}
              </button>
              <button class="btn btn-outline-danger btn-sm" @click="logout">Logout</button>
            </div>
          </div>

          <p v-if="loading">Loading...</p>

          <div v-else>
            <div class="row text-center mb-4">
              <div class="col"><div class="card p-3"><div class="fs-4">{{ stats.total_students }}</div><div class="text-muted">Students</div></div></div>
              <div class="col"><div class="card p-3"><div class="fs-4">{{ stats.total_companies }}</div><div class="text-muted">Companies</div></div></div>
              <div class="col"><div class="card p-3"><div class="fs-4">{{ stats.total_job_positions }}</div><div class="text-muted">Job Postings</div></div></div>
              <div class="col"><div class="card p-3"><div class="fs-4">{{ stats.total_applications }}</div><div class="text-muted">Applications</div></div></div>
            </div>

            <ul class="nav nav-tabs mb-3">
              <li class="nav-item" v-for="tab in ['companies', 'students', 'jobs', 'applications']" :key="tab">
                <a class="nav-link" :class="{ active: activeTab === tab }" href="#" @click.prevent="activeTab = tab">
                  {{ tab.charAt(0).toUpperCase() + tab.slice(1) }}
                </a>
              </li>
            </ul>

            <AdminCompanies v-if="activeTab === 'companies'" />
            <AdminStudents v-if="activeTab === 'students'" />
            <AdminJobPositions v-if="activeTab === 'jobs'" />
            <AdminApplications v-if="activeTab === 'applications'" />
          </div>
        </div>
    `,
};