import { apiFetch } from "/src/api.js";

export default {
    props: { jobId: { type: Number, required: true }, jobTitle: { type: String, required: true } },
    emits: ["back"],
    data() {
        return { applications: [], loading: true, feedbackDrafts: {} };
    },
    async mounted() {
        await this.load();
    },
    methods: {
        async load() {
            this.loading = true;
            this.applications = await apiFetch(`/api/company/job-positions/${this.jobId}/applications`);
            this.applications.forEach(a => { this.feedbackDrafts[a.id] = a.feedback || ""; });
            this.loading = false;
        },
        async setStatus(application, status) {
            await apiFetch(`/api/company/applications/${application.id}/status`, {
                method: "POST",
                body: JSON.stringify({ status, feedback: this.feedbackDrafts[application.id] }),
            });
            await this.load();
        },
        async scheduleInterview(application) {
            const when = prompt("Interview date & time (e.g. 2026-08-15T10:30)");
            if (!when) return;
            try {
                await apiFetch(`/api/company/applications/${application.id}/schedule-interview`, {
                    method: "POST",
                    body: JSON.stringify({ interview_datetime: when }),
                });
                await this.load();
            } catch (err) {
                alert(err.data?.error || "Could not schedule interview.");
            }
        },
        statusBadge(status) {
            const map = { applied: "bg-primary", shortlisted: "bg-info text-dark", selected: "bg-success", rejected: "bg-danger" };
            return map[status] || "bg-secondary";
        },
    },
    template: `
        <div>
          <button class="btn btn-sm btn-outline-secondary mb-3" @click="$emit('back')">&larr; Back to Drives</button>
          <h5 class="mb-3">Applicants for "{{ jobTitle }}"</h5>

          <p v-if="loading">Loading applicants...</p>
          <div v-else>
            <div v-if="applications.length === 0" class="text-muted">No applications received yet.</div>

            <div v-for="a in applications" :key="a.id" class="card p-3 mb-3">
              <h6 class="mb-1">{{ a.student_name }} <span class="badge" :class="statusBadge(a.status)">{{ a.status }}</span></h6>
              <small class="text-muted">{{ a.student_email }} · {{ a.branch || "-" }} · CGPA {{ a.cgpa ?? "-" }}</small>
              <div v-if="a.interview_datetime" class="mt-1">
                <small class="text-info">Interview scheduled: {{ a.interview_datetime.replace('T', ' ').slice(0, 16) }}</small>
              </div>

              <textarea v-model="feedbackDrafts[a.id]" class="form-control mt-2" rows="2" placeholder="Feedback for this applicant (optional)"></textarea>

              <div class="d-flex gap-2 mt-2 flex-wrap">
                <button class="btn btn-sm btn-info" :disabled="a.status === 'shortlisted'" @click="setStatus(a, 'shortlisted')">Shortlist</button>
                <button class="btn btn-sm btn-success" :disabled="a.status === 'selected'" @click="setStatus(a, 'selected')">Select</button>
                <button class="btn btn-sm btn-danger" :disabled="a.status === 'rejected'" @click="setStatus(a, 'rejected')">Reject</button>
                <button class="btn btn-sm btn-outline-primary" :disabled="a.status !== 'shortlisted'" @click="scheduleInterview(a)">
                  Schedule Interview
                </button>
              </div>
            </div>
          </div>
        </div>
    `,
};