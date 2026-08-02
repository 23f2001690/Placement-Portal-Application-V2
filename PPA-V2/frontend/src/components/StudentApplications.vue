import { apiFetch, apiDownload } from "/src/api.js";

export default {
    data() {
        return { applications: [], loading: true, exporting: false, exportMessage: "" };
    },
    async mounted() {
        this.applications = await apiFetch("/api/student/applications");
        this.loading = false;
    },
    methods: {
        async downloadOfferLetter(application) {
            try {
                await apiDownload(`/api/student/applications/${application.id}/offer-letter`, `offer_letter_${application.id}.txt`);
            } catch (err) {
                alert(err.message || "Could not download offer letter.");
            }
        },
        async exportHistory() {
            this.exporting = true;
            this.exportMessage = "Export started...";
            try {
                const { task_id } = await apiFetch("/api/student/export", { method: "POST" });
                this.pollExport(task_id);
            } catch (err) {
                this.exportMessage = "Could not start export.";
                this.exporting = false;
            }
        },
        async pollExport(taskId) {
            const status = await apiFetch(`/api/student/export/status/${taskId}`);
            if (status.state === "SUCCESS") {
                this.exportMessage = "Export ready - downloading...";
                this.exporting = false;
                await apiDownload(`/api/student/export/download/${status.result.filename}`, status.result.filename);
                alert("Your application history CSV has been downloaded.");
            } else if (status.state === "FAILURE") {
                this.exportMessage = "Export failed.";
                this.exporting = false;
            } else {
                setTimeout(() => this.pollExport(taskId), 1500);
            }
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
          <div class="d-flex justify-content-between align-items-center mb-3">
            <span v-if="exportMessage" class="text-muted small">{{ exportMessage }}</span>
            <button class="btn btn-sm btn-outline-secondary ms-auto" :disabled="exporting" @click="exportHistory">
              {{ exporting ? "Exporting..." : "Export CSV" }}
            </button>
          </div>

          <p v-if="loading">Loading applications...</p>
          <div v-else>
            <div v-if="applications.length === 0" class="text-muted">You haven't applied to any drives yet.</div>

            <div v-for="a in applications" :key="a.id" class="card p-3 mb-3">
              <div class="d-flex justify-content-between">
                <h6 class="mb-1">{{ a.job_title }} <span class="badge" :class="statusBadge(a.status)">{{ a.status }}</span></h6>
                <strong>{{ a.company_name }}</strong>
              </div>
              <small class="text-muted">Applied on {{ a.applied_on.slice(0, 10) }}</small>

              <div v-if="a.interview_datetime" class="mt-1">
                <small class="text-info">Interview scheduled: {{ a.interview_datetime.replace('T', ' ').slice(0, 16) }}</small>
              </div>
              <div v-if="a.feedback" class="mt-1">
                <small><strong>Feedback:</strong> {{ a.feedback }}</small>
              </div>
              <div v-if="a.status === 'placed'" class="mt-1">
                <small><strong>Package:</strong> {{ a.package_offered || "-" }}
                  <span v-if="a.joining_date"> · Joining {{ a.joining_date }}</span>
                </small>
              </div>

              <div v-if="a.status === 'placed'" class="mt-2">
                <button class="btn btn-sm btn-outline-success" @click="downloadOfferLetter(a)">Download Offer Letter</button>
              </div>
            </div>
          </div>
        </div>
    `,
};