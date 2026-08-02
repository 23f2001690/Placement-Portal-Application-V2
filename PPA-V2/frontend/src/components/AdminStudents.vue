import { apiFetch } from "/src/api.js";
import ApplicationHistoryModal from "/src/components/ApplicationHistoryModal.vue";

export default {
    components: { ApplicationHistoryModal },
    data() {
        return { students: [], search: "", loading: true, historyData: null };
    },
    async mounted() {
        await this.load();
    },
    methods: {
        async load() {
            this.loading = true;
            const query = this.search ? `?search=${encodeURIComponent(this.search)}` : "";
            this.students = await apiFetch(`/api/admin/students${query}`);
            this.loading = false;
        },
        async remove(student) {
            if (!confirm(`Remove ${student.full_name} permanently?`)) return;
            await apiFetch(`/api/admin/students/${student.id}`, { method: "DELETE" });
            await this.load();
        },
        async toggleBlacklist(student) {
            await apiFetch(`/api/admin/students/${student.id}/blacklist`, { method: "POST" });
            await this.load();
        },
        async viewHistory(student) {
            this.historyData = await apiFetch(`/api/admin/students/${student.id}/history`);
        },
    },
    template: `
        <div>
          <div class="d-flex gap-2 mb-3">
            <input v-model="search" @keyup.enter="load" class="form-control" placeholder="Search by name, ID or email" />
            <button class="btn btn-outline-primary" @click="load">Search</button>
          </div>
          <p v-if="loading">Loading students...</p>
          <table v-else class="table table-bordered align-middle">
            <thead class="table-light">
              <tr>
                <th>ID</th><th>Name</th><th>Branch</th><th>CGPA</th><th>Email</th><th>Blacklisted</th><th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="s in students" :key="s.id">
                <td>{{ s.id }}</td>
                <td>{{ s.full_name }}</td>
                <td>{{ s.branch || "-" }}</td>
                <td>{{ s.cgpa ?? "-" }}</td>
                <td>{{ s.email }}</td>
                <td>{{ s.is_blacklisted ? "Yes" : "No" }}</td>
                <td class="d-flex gap-1 flex-wrap">
                  <button class="btn btn-sm btn-outline-primary" @click="viewHistory(s)">History</button>
                  <button class="btn btn-sm btn-outline-dark" @click="toggleBlacklist(s)">
                    {{ s.is_blacklisted ? "Unblacklist" : "Blacklist" }}
                  </button>
                  <button class="btn btn-sm btn-outline-danger" @click="remove(s)">Remove</button>
                </td>
              </tr>
              <tr v-if="students.length === 0"><td colspan="7" class="text-center text-muted">No students found</td></tr>
            </tbody>
          </table>

          <ApplicationHistoryModal
            v-if="historyData"
            :profile="historyData.profile"
            :applications="historyData.applications"
            @close="historyData = null"
          />
        </div>
    `,
};