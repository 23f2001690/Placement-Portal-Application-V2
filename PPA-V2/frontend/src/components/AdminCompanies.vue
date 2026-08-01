import { apiFetch } from "/src/api.js";

export default {
    data() {
        return { companies: [], search: "", loading: true };
    },
    async mounted() {
        await this.load();
    },
    methods: {
        async load() {
            this.loading = true;
            const query = this.search ? `?search=${encodeURIComponent(this.search)}` : "";
            this.companies = await apiFetch(`/api/admin/companies${query}`);
            this.loading = false;
        },
        async approve(company) {
            await apiFetch(`/api/admin/companies/${company.id}/approve`, { method: "POST" });
            await this.load();
        },
        async reject(company) {
            await apiFetch(`/api/admin/companies/${company.id}/reject`, { method: "POST" });
            await this.load();
        },
        async remove(company) {
            if (!confirm(`Remove ${company.company_name} permanently?`)) return;
            await apiFetch(`/api/admin/companies/${company.id}`, { method: "DELETE" });
            await this.load();
        },
        async toggleBlacklist(company) {
            await apiFetch(`/api/admin/companies/${company.id}/blacklist`, { method: "POST" });
            await this.load();
        },
        statusBadge(status) {
            const map = { approved: "bg-success", pending: "bg-warning text-dark", rejected: "bg-danger" };
            return map[status] || "bg-secondary";
        },
    },
    template: `
        <div>
          <div class="d-flex gap-2 mb-3">
            <input v-model="search" @keyup.enter="load" class="form-control" placeholder="Search by name or industry" />
            <button class="btn btn-outline-primary" @click="load">Search</button>
          </div>
          <p v-if="loading">Loading companies...</p>
          <table v-else class="table table-bordered align-middle">
            <thead class="table-light">
              <tr>
                <th>Company</th><th>Industry</th><th>Email</th><th>Status</th><th>Blacklisted</th><th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="c in companies" :key="c.id">
                <td>{{ c.company_name }}</td>
                <td>{{ c.industry || "-" }}</td>
                <td>{{ c.email }}</td>
                <td><span class="badge" :class="statusBadge(c.approval_status)">{{ c.approval_status }}</span></td>
                <td>{{ c.is_blacklisted ? "Yes" : "No" }}</td>
                <td class="d-flex gap-1 flex-wrap">
                  <button class="btn btn-sm btn-success" :disabled="c.approval_status === 'approved'" @click="approve(c)">Approve</button>
                  <button class="btn btn-sm btn-danger" :disabled="c.approval_status === 'rejected'" @click="reject(c)">Reject</button>
                  <button class="btn btn-sm btn-outline-dark" @click="toggleBlacklist(c)">
                    {{ c.is_blacklisted ? "Unblacklist" : "Blacklist" }}
                  </button>
                  <button class="btn btn-sm btn-outline-danger" @click="remove(c)">Remove</button>
                </td>
              </tr>
              <tr v-if="companies.length === 0"><td colspan="6" class="text-center text-muted">No companies found</td></tr>
            </tbody>
          </table>
        </div>
    `,
};