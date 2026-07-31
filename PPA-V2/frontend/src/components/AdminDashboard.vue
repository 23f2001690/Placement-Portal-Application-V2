<template>
  <div class="container py-4">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3>Admin Dashboard</h3>
      <button class="btn btn-outline-danger btn-sm" @click="logout">Logout</button>
    </div>

    <p v-if="loading">Loading...</p>

    <div v-else>
      <div class="row text-center mb-4">
        <div class="col">
          <div class="card p-3">
            <div class="fs-4">{{ stats.total_students }}</div>
            <div class="text-muted">Students</div>
          </div>
        </div>

        <div class="col">
          <div class="card p-3">
            <div class="fs-4">{{ stats.total_companies }}</div>
            <div class="text-muted">Companies</div>
          </div>
        </div>

        <div class="col">
          <div class="card p-3">
            <div class="fs-4">{{ stats.total_job_positions }}</div>
            <div class="text-muted">Job Postings</div>
          </div>
        </div>

        <div class="col">
          <div class="card p-3">
            <div class="fs-4">{{ stats.total_applications }}</div>
            <div class="text-muted">Applications</div>
          </div>
        </div>
      </div>

      <ul class="nav nav-tabs mb-3">
        <li class="nav-item" v-for="tab in ['companies', 'students', 'jobs', 'applications']" :key="tab">
          <a class="nav-link" :class="{ active: activeTab === tab }" href="#" @click.prevent="activeTab = tab">
            {{ tab.charAt(0).toUpperCase() + tab.slice(1) }}
          </a>
        </li>
      </ul>

      <AdminCompanies v-if="activeTab === 'companies'" />
      <AdminStudents v-if="activeTab === 'students'" />
      <AdminJobPositions v-if="activeTab === 'jobs'" />
      <AdminApplications v-if="activeTab === 'applications'" />
    </div>
  </div>
</template>

<script>
import { apiFetch, logout } from "/src/api.js";
import AdminCompanies from "/src/components/AdminCompanies.vue";
import AdminStudents from "/src/components/AdminStudents.vue";
import AdminJobPositions from "/src/components/AdminJobPositions.vue";
import AdminApplications from "/src/components/AdminApplications.vue";

export default {
  components: { AdminCompanies, AdminStudents, AdminJobPositions, AdminApplications },
  data() {
    return { loading: true, stats: null, activeTab: "companies" };
  },
  async mounted() {
    try {
      this.stats = await apiFetch("/api/admin/stats");
    } catch (e) {
      window.location.hash = "/login";
    } finally {
      this.loading = false;
    }
  },
  methods: { logout }
};
</script>
