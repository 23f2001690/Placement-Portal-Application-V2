import { apiFetch } from "/src/api.js";

export default {
    data() {
        return { applications: [], loading: true };
    },
    async mounted() {
        this.applications = await apiFetch("/api/admin/applications");
        this.loading = false;
    },
    methods: {
        statusBadge(status) {
            const map = { applied: "bg-primary", shortlisted: "bg-info text-dark", selected: "bg-success", rejected: "bg-danger" };
            return map[status] || "bg-secondary";
        },
    },
    template: `
        <div>
          <p v-if="loading">Loading applications...</p>
          <table v-else class="table table-bordered align-middle">
            <thead class="table-light">
              <tr><th>Student</th><th>Job Title</th><th>Company</th><th>Status</th><th>Applied On</th></tr>
            </thead>
            <tbody>
              <tr v-for="a in applications" :key="a.id">
                <td>{{ a.student_name }}</td>
                <td>{{ a.job_title }}</td>
                <td>{{ a.company_name }}</td>
                <td><span class="badge" :class="statusBadge(a.status)">{{ a.status }}</span></td>
                <td>{{ a.applied_on.slice(0, 10) }}</td>
              </tr>
              <tr v-if="applications.length === 0"><td colspan="5" class="text-center text-muted">No applications yet</td></tr>
            </tbody>
          </table>
        </div>
    `,
};