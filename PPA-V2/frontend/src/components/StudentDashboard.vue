import { apiFetch, logout } from "/src/api.js";
import StudentJobPositions from "/src/components/StudentJobPositions.vue";
import StudentApplications from "/src/components/StudentApplications.vue";
import StudentProfile from "/src/components/StudentProfile.vue";

export default {
    components: { StudentJobPositions, StudentApplications, StudentProfile },
    data() {
        return { loading: true, profile: null, activeTab: "drives" };
    },
    async mounted() {
        try {
            this.profile = await apiFetch("/api/student/profile");
        } catch (e) {
            window.location.hash = "/login";
        } finally {
            this.loading = false;
        }
    },
    methods: { logout },
    template: `
        <div class="container py-4">
          <div class="d-flex justify-content-between align-items-center mb-4">
            <h3>Student Dashboard</h3>
            <button class="btn btn-outline-danger btn-sm" @click="logout">Logout</button>
          </div>

          <p v-if="loading">Loading...</p>

          <div v-else>
            <p class="text-muted">Welcome, {{ profile.full_name }}</p>

            <ul class="nav nav-tabs mb-3">
              <li class="nav-item" v-for="tab in ['drives', 'applications', 'profile']" :key="tab">
                <a class="nav-link" :class="{ active: activeTab === tab }" href="#" @click.prevent="activeTab = tab">
                  {{ tab.charAt(0).toUpperCase() + tab.slice(1) }}
                </a>
              </li>
            </ul>

            <StudentJobPositions v-if="activeTab === 'drives'" />
            <StudentApplications v-if="activeTab === 'applications'" />
            <StudentProfile v-if="activeTab === 'profile'" />
          </div>
        </div>
    `,
};