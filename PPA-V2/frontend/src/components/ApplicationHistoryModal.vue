export default {
    props: {
        profile: { type: Object, required: true },
        applications: { type: Array, required: true },
    },
    emits: ["close"],
    methods: {
        statusBadge(status) {
            const map = {
                applied: "bg-primary", shortlisted: "bg-info text-dark", interview: "bg-warning text-dark",
                offer: "bg-success", placed: "bg-dark", rejected: "bg-danger",
            };
            return map[status] || "bg-secondary";
        },
    },
    template: `
        <div class="modal d-block" style="background: rgba(0,0,0,0.5);" @click.self="$emit('close')">
          <div class="modal-dialog modal-lg">
            <div class="modal-content p-3">
              <div class="d-flex justify-content-between align-items-center mb-3">
                <h5 class="mb-0">{{ profile.full_name }}'s History</h5>
                <button class="btn-close" @click="$emit('close')"></button>
              </div>
              <p class="text-muted mb-3">
                {{ profile.branch || "-" }} · CGPA {{ profile.cgpa ?? "-" }} · {{ profile.email }}
              </p>

              <div v-if="applications.length === 0" class="text-muted">No applications on record.</div>

              <table v-else class="table table-sm table-bordered">
                <thead class="table-light">
                  <tr><th>Job Title</th><th>Company</th><th>Status</th><th>Applied On</th><th>Placement</th></tr>
                </thead>
                <tbody>
                  <tr v-for="a in applications" :key="a.id">
                    <td>{{ a.job_title }}</td>
                    <td>{{ a.company_name }}</td>
                    <td><span class="badge" :class="statusBadge(a.status)">{{ a.status }}</span></td>
                    <td>{{ a.applied_on.slice(0, 10) }}</td>
                    <td>
                      <span v-if="a.status === 'placed'">{{ a.package_offered || "-" }}</span>
                      <span v-else>-</span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
    `,
};