import { apiFetch } from "/src/api.js";

export default {
    emits: ["view-applicants"],
    data() {
        return {
            jobs: [],
            loading: true,
            showForm: false,
            errorMessage: "",
            form: {
                title: "", description: "", salary: "", skills_required: "",
                min_cgpa: null, eligible_branches: "", eligible_year: null, application_deadline: "",
            },
        };
    },
    async mounted() {
        await this.load();
    },
    methods: {
        async load() {
            this.loading = true;
            this.jobs = await apiFetch("/api/company/job-positions");
            this.loading = false;
        },
        async submitJob() {
            this.errorMessage = "";
            try {
                await apiFetch("/api/company/job-positions", {
                    method: "POST",
                    body: JSON.stringify(this.form),
                });
                this.showForm = false;
                this.form = {
                    title: "", description: "", salary: "", skills_required: "",
                    min_cgpa: null, eligible_branches: "", eligible_year: null, application_deadline: "",
                };
                await this.load();
            } catch (err) {
                this.errorMessage = err.data?.error || "Could not create drive.";
            }
        },
        async closeJob(job) {
            if (!confirm(`Close drive "${job.title}"? Students won't be able to apply anymore.`)) return;
            await apiFetch(`/api/company/job-positions/${job.id}/close`, { method: "POST" });
            await this.load();
        },
        statusBadge(status) {
            const map = { approved: "bg-success", pending: "bg-warning text-dark", rejected: "bg-danger", closed: "bg-secondary" };
            return map[status] || "bg-secondary";
        },
    },
    template: `
        <div>
          <div class="d-flex justify-content-between align-items-center mb-3">
            <h5 class="mb-0">My Drives</h5>
            <button class="btn btn-primary btn-sm" @click="showForm = !showForm">
              {{ showForm ? "Cancel" : "+ Post New Drive" }}
            </button>
          </div>

          <div v-if="showForm" class="card p-3 mb-4">
            <div v-if="errorMessage" class="alert alert-danger py-2">{{ errorMessage }}</div>
            <form @submit.prevent="submitJob">
              <div class="mb-2">
                <label class="form-label">Job Title</label>
                <input v-model="form.title" class="form-control" required />
              </div>
              <div class="mb-2">
                <label class="form-label">Job Description</label>
                <textarea v-model="form.description" class="form-control" rows="3"></textarea>
              </div>
              <div class="row">
                <div class="col mb-2">
                  <label class="form-label">Salary / Package</label>
                  <input v-model="form.salary" class="form-control" placeholder="e.g. 8 LPA" />
                </div>
                <div class="col mb-2">
                  <label class="form-label">Skills Required</label>
                  <input v-model="form.skills_required" class="form-control" placeholder="Python, SQL" />
                </div>
              </div>
              <div class="row">
                <div class="col mb-2">
                  <label class="form-label">Min CGPA</label>
                  <input v-model.number="form.min_cgpa" type="number" step="0.01" class="form-control" />
                </div>
                <div class="col mb-2">
                  <label class="form-label">Eligible Branches</label>
                  <input v-model="form.eligible_branches" class="form-control" placeholder="CSE,IT,ECE" />
                </div>
                <div class="col mb-2">
                  <label class="form-label">Eligible Year</label>
                  <input v-model.number="form.eligible_year" type="number" class="form-control" />
                </div>
              </div>
              <div class="mb-3">
                <label class="form-label">Application Deadline</label>
                <input v-model="form.application_deadline" type="datetime-local" class="form-control" />
              </div>
              <button type="submit" class="btn btn-success">Submit for Admin Approval</button>
            </form>
          </div>

          <p v-if="loading">Loading drives...</p>
          <table v-else class="table table-bordered align-middle">
            <thead class="table-light">
              <tr><th>Title</th><th>Salary</th><th>Applicants</th><th>Status</th><th>Actions</th></tr>
            </thead>
            <tbody>
              <tr v-for="j in jobs" :key="j.id">
                <td>{{ j.title }}</td>
                <td>{{ j.salary || "-" }}</td>
                <td>{{ j.applicant_count }}</td>
                <td><span class="badge" :class="statusBadge(j.status)">{{ j.status }}</span></td>
                <td class="d-flex gap-1 flex-wrap">
                  <button class="btn btn-sm btn-outline-primary" @click="$emit('view-applicants', { id: j.id, title: j.title })">
                    View Applicants
                  </button>
                  <button v-if="j.status === 'approved'" class="btn btn-sm btn-outline-secondary" @click="closeJob(j)">
                    Close
                  </button>
                </td>
              </tr>
              <tr v-if="jobs.length === 0"><td colspan="5" class="text-center text-muted">No drives posted yet</td></tr>
            </tbody>
          </table>
        </div>
    `,
};