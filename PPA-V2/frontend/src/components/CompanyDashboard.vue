import { apiFetch, logout } from "/src/api.js";
import CompanyJobPositions from "/src/components/CompanyJobPositions.vue";
import CompanyApplicants from "/src/components/CompanyApplicants.vue";

export default {
    components: { CompanyJobPositions, CompanyApplicants },
    data() {
        return { loading: true, profile: null, stats: null, selectedJob: null };
    },
    async mounted() {
        try {
            this.profile = await apiFetch("/api/company/profile");
            this.stats = await apiFetch("/api/company/stats");
        } catch (e) {
            window.location.hash = "/login";
        } finally {
            this.loading = false;
        }
    },
    methods: {
        logout,
        statusBadge(status) {
            const map = { approved: "bg-success", pending: "bg-warning text-dark", rejected: "bg-danger" };
            return map[status] || "bg-secondary";
        },
        viewApplicants(job) {
            this.selectedJob = job;
        },
        backToJobs() {
            this.selectedJob = null;
        },
    },
    template: `
        <div class="container py-4">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h3>Company Dashboard</h3>
            <button class="btn btn-outline-danger btn-sm" @click="logout">Logout</button>
          </div>

          <p v-if="loading">Loading...</p>

          <div v-else>
            <div class="card p-3 mb-4">
              <h5 class="mb-1">{{ profile.company_name }}</h5>
              <span class="badge" :class="statusBadge(profile.approval_status)">{{ profile.approval_status }}</span>
            </div>

            <div v-if="profile.approval_status !== 'approved'" class="alert alert-info">
              Your company profile is <strong>{{ profile.approval_status }}</strong>.
              You'll be able to post drives and manage applicants once the placement cell approves your registration.
            </div>

            <div v-else>
              <div class="row text-center mb-4">
                <div class="col"><div class="card p-3"><div class="fs-4">{{ stats.total_job_positions }}</div><div class="text-muted">Job Postings</div></div></div>
                <div class="col"><div class="card p-3"><div class="fs-4">{{ stats.total_applications }}</div><div class="text-muted">Applications Received</div></div></div>
                <div class="col"><div class="card p-3"><div class="fs-4">{{ stats.total_shortlisted }}</div><div class="text-muted">Shortlisted</div></div></div>
              </div>

              <CompanyApplicants
                v-if="selectedJob"
                :job-id="selectedJob.id"
                :job-title="selectedJob.title"
                @back="backToJobs"
              />
              <CompanyJobPositions v-else @view-applicants="viewApplicants" />
            </div>
          </div>
        </div>
    `,
};
