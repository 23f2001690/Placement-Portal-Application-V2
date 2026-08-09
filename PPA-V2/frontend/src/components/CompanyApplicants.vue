
import { apiFetch, apiOpenFile } from "/src/api.js";
import ApplicationHistoryModal from "/src/components/ApplicationHistoryModal.vue";

export default {
    components: { ApplicationHistoryModal },
    props: { jobId: { type: Number, required: true }, jobTitle: { type: String, required: true } },
    emits: ["back"],
    data() {
        return { applications: [], loading: true, feedbackDrafts: {}, historyData: null };
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
            const body = { status, feedback: this.feedbackDrafts[application.id] };
            if (status === "placed") {
                body.package_offered = prompt("Package offered:", application.package_offered || "") || undefined;
                body.joining_date = prompt("Joining date (YYYY-MM-DD):") || undefined;
            }
            await apiFetch(`/api/company/applications/${application.id}/status`, {
                method: "POST",
                body: JSON.stringify(body),
            });
            await this.load();
        },
        async viewResume(application) {
            try {
                await apiOpenFile(`/api/company/applications/${application.id}/resume`);
            } catch (err) {
                alert(err.message || "Could not open resume.");
            }
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
        async viewHistory(application) {
            this.historyData = await apiFetch(`/api/company/students/${application.student_id}/history`);
        },
        statusBadge(status) {
            const map = {
                applied: "bg-primary", shortlisted: "bg-info text-dark", interview: "bg-warning text-dark",
                offer: "bg-success", placed: "bg-dark", rejected: "bg-danger",
            };
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
              <h6 class="mb-1 d-flex align-items-center gap-2">
                {{ a.student_name }}
                <span class="badge" :class="statusBadge(a.status)">{{ a.status }}</span>
                <button class="btn btn-sm btn-outline-info ms-2" :disabled="!a.resume_path" @click="viewResume(a)">
                  {{ a.resume_path ? "View Resume" : "No Resume" }}
                </button>
              </h6>
              <small class="text-muted">{{ a.student_email }} · {{ a.branch || "-" }} · CGPA {{ a.cgpa ?? "-" }}</small>
              <div v-if="a.interview_datetime" class="mt-1">
                <small class="text-info">Interview: {{ a.interview_datetime.replace('T', ' ').slice(0, 16) }}</small>
              </div>

              <textarea v-model="feedbackDrafts[a.id]" class="form-control mt-2" rows="2" placeholder="Feedback for this applicant (optional)"></textarea>

              <div class="d-flex gap-2 mt-2 flex-wrap">
                <button class="btn btn-sm btn-info" :disabled="a.status === 'shortlisted'" @click="setStatus(a, 'shortlisted')">Shortlist</button>
                <button class="btn btn-sm btn-outline-primary" :disabled="a.status === 'rejected' || a.status === 'placed'" @click="scheduleInterview(a)">
                  Schedule Interview
                </button>
                <button class="btn btn-sm btn-success" :disabled="a.status === 'offer' || a.status === 'placed'" @click="setStatus(a, 'offer')">Offer</button>
                <button class="btn btn-sm btn-dark" :disabled="a.status === 'placed'" @click="setStatus(a, 'placed')">Mark Placed</button>
                <button class="btn btn-sm btn-danger" :disabled="a.status === 'rejected'" @click="setStatus(a, 'rejected')">Reject</button>
                <button class="btn btn-sm btn-outline-secondary" @click="viewHistory(a)">Full History</button>
              </div>
            </div>
          </div>

          <ApplicationHistoryModal
            v-if="historyData"
            :profile="historyData.profile"
            :applications="historyData.applications"
            @close="historyData = null"
          />
        </div>
    `,
};