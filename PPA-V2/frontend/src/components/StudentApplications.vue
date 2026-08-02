import { apiFetch, apiDownload } from "/src/api.js";

export default {
    data() {
        return { applications: [], loading: true };
    },
    async mounted() {
        this.applications = await apiFetch("/api/student/applications");
        this.loading = false;
    },
    methods: {
        async downloadOfferLetter(application) {
            try {
                await apiDownload(
                    `/api/student/applications/${application.id}/offer-letter`,
                    `offer_letter_${application.id}.txt`
                );
            } catch (err) {
                alert(err.message || "Could not download offer letter.");
            }
        },
        statusBadge(status) {
            const map = { applied: "bg-primary", shortlisted: "bg-info text-dark", selected: "bg-success", rejected: "bg-danger" };
            return map[status] || "bg-secondary";
        },
    },
    template: `
        <div>
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

              <div v-if="a.status === 'selected'" class="mt-2">
                <button class="btn btn-sm btn-outline-success" @click="downloadOfferLetter(a)">Download Offer Letter</button>
              </div>
            </div>
          </div>
        </div>
    `,
};