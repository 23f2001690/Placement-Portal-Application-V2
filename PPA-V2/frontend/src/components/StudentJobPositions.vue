import { apiFetch } from "/src/api.js";

export default {
    data() {
        return { jobs: [], search: "", loading: true };
    },
    async mounted() {
        await this.load();
    },
    methods: {
        async load() {
            this.loading = true;
            const query = this.search ? `?search=${encodeURIComponent(this.search)}` : "";
            this.jobs = await apiFetch(`/api/student/job-positions${query}`);
            this.loading = false;
        },
        async apply(job) {
            try {
                await apiFetch(`/api/student/job-positions/${job.id}/apply`, { method: "POST" });
                await this.load();
            } catch (err) {
                alert(err.data?.error || err.message || "Could not apply.");
            }
        },
        statusBadge(status) {
            const map = { approved: "bg-success", closed: "bg-secondary" };
            return map[status] || "bg-secondary";
        },
    },
    template: `
        <div>
          <div class="d-flex gap-2 mb-3">
            <input v-model="search" @keyup.enter="load" class="form-control" placeholder="Search by title or skills" />
            <button class="btn btn-outline-primary" @click="load">Search</button>
          </div>

          <p v-if="loading">Loading drives...</p>
          <div v-else>
            <div v-if="jobs.length === 0" class="text-muted">No drives available right now.</div>

            <div v-for="j in jobs" :key="j.id" class="card p-3 mb-3">
              <div class="d-flex justify-content-between">
                <h6 class="mb-1">{{ j.title }} <span class="badge" :class="statusBadge(j.status)">{{ j.status }}</span></h6>
                <strong>{{ j.company_name }}</strong>
              </div>
              <p class="mb-1">{{ j.description || "No description provided." }}</p>
              <small class="text-muted">
                Salary: {{ j.salary || "-" }} · Skills: {{ j.skills_required || "-" }} ·
                Min CGPA: {{ j.min_cgpa ?? "-" }} · Deadline: {{ j.application_deadline ? j.application_deadline.slice(0,10) : "-" }}
              </small>

              <div class="mt-2">
                <span v-if="j.already_applied" class="badge bg-primary">Already Applied</span>
                <span v-else-if="j.status !== 'approved'" class="badge bg-secondary">Drive Closed</span>
                <span v-else-if="!j.is_eligible" class="badge bg-warning text-dark">{{ j.eligibility_reason }}</span>
                <button v-else class="btn btn-sm btn-success" @click="apply(j)">Apply</button>
              </div>
            </div>
          </div>
        </div>
    `,
};