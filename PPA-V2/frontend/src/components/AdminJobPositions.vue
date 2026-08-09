import { apiFetch } from "/src/api.js";

export default {
    data() {
        return { jobs: [], statusFilter: "", search: "", loading: true };
    },
    async mounted() {
        await this.load();
    },
    methods: {
        async load() {
            this.loading = true;
            const params = new URLSearchParams();
            if (this.statusFilter) params.set("status", this.statusFilter);
            if (this.search) params.set("search", this.search);
            const query = params.toString() ? `?${params.toString()}` : "";
            this.jobs = await apiFetch(`/api/admin/job-positions${query}`);
            this.loading = false;
        },
        async approve(job) {
            await apiFetch(`/api/admin/job-positions/${job.id}/approve`, { method: "POST" });
            await this.load();
        },
        async reject(job) {
            await apiFetch(`/api/admin/job-positions/${job.id}/reject`, { method: "POST" });
            await this.load();
        },
        async remove(job) {
            if (!confirm(`Remove drive "${job.title}" permanently?`)) return;
            await apiFetch(`/api/admin/job-positions/${job.id}`, { method: "DELETE" });
            await this.load();
        },
        statusBadge(status) {
            const map = { approved: "bg-success", pending: "bg-warning text-dark", rejected: "bg-danger", closed: "bg-secondary" };
            return map[status] || "bg-secondary";
        },
    },
    template: `
        <div>
          <div class="d-flex gap-2 mb-3">
            <input v-model="search" @keyup.enter="load" class="form-control" placeholder="Search by drive title or company" />
            <button class="btn btn-outline-primary" @click="load">Search</button>
            <select v-model="statusFilter" @change="load" class="form-select" style="max-width: 200px;">
              <option value="">All statuses</option>
              <option value="pending">Pending</option>
              <option value="approved">Approved</option>
              <option value="rejected">Rejected</option>
              <option value="closed">Closed</option>
            </select>
          </div>
          <p v-if="loading">Loading job postings...</p>
          <table v-else class="table table-bordered align-middle">
            <thead class="table-light">
              <tr><th>Title</th><th>Company</th><th>Salary</th><th>Applicants</th><th>Status</th><th>Actions</th></tr>
            </thead>
            <tbody>
              <tr v-for="j in jobs" :key="j.id">
                <td>{{ j.title }}</td>
                <td>{{ j.company_name }}</td>
                <td>{{ j.salary || "-" }}</td>
                <td>{{ j.applicant_count }}</td>
                <td><span class="badge" :class="statusBadge(j.status)">{{ j.status }}</span></td>
                <td class="d-flex gap-1 flex-wrap">
                  <button class="btn btn-sm btn-success" :disabled="j.status === 'approved'" @click="approve(j)">Approve</button>
                  <button class="btn btn-sm btn-danger" :disabled="j.status === 'rejected'" @click="reject(j)">Reject</button>
                  <button class="btn btn-sm btn-outline-danger" @click="remove(j)">Remove</button>
                </td>
              </tr>
              <tr v-if="jobs.length === 0"><td colspan="6" class="text-center text-muted">No job postings found</td></tr>
            </tbody>
          </table>
        </div>
    `,
};