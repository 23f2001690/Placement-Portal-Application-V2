<template>
  <div class="d-flex justify-content-center align-items-center vh-100 bg-light">
    <div class="card shadow-sm p-4" style="width: 420px;">
      <h4 class="mb-3 text-center">Student Registration</h4>

      <div v-if="errorMessage" class="alert alert-danger py-2">
        {{ errorMessage }}
      </div>

      <div v-if="successMessage" class="alert alert-success py-2">
        {{ successMessage }}
      </div>

      <form @submit.prevent="handleRegister">
        <div class="mb-2">
          <label class="form-label">Full Name</label>
          <input v-model="form.full_name" class="form-control" required />
        </div>

        <div class="mb-2">
          <label class="form-label">Email</label>
          <input v-model="form.email" type="email" class="form-control" required />
        </div>

        <div class="mb-2">
          <label class="form-label">Password</label>
          <input v-model="form.password" type="password" class="form-control" required />
        </div>

        <div class="row">
          <div class="col mb-2">
            <label class="form-label">Branch</label>
            <input v-model="form.branch" class="form-control" placeholder="CSE" />
          </div>

          <div class="col mb-2">
            <label class="form-label">Year</label>
            <input v-model.number="form.year_of_study" type="number" class="form-control" />
          </div>
        </div>

        <div class="mb-2">
          <label class="form-label">CGPA</label>
          <input v-model.number="form.cgpa" type="number" step="0.01" class="form-control" />
        </div>

        <div class="mb-3">
          <label class="form-label">Skills (comma separated)</label>
          <input v-model="form.skills" class="form-control" placeholder="Python, SQL" />
        </div>

        <button type="submit" class="btn btn-primary w-100" :disabled="loading">
          {{ loading ? "Registering..." : "Register" }}
        </button>
      </form>

      <p class="text-center mt-3 mb-0">
        Already have an account? <a href="#/login">Login</a>
      </p>
    </div>
  </div>
</template>

<script>
import { apiFetch } from "/src/api.js";

export default {
  data() {
    return {
      form: {
        full_name: "",
        email: "",
        password: "",
        branch: "",
        year_of_study: null,
        cgpa: null,
        skills: ""
      },
      loading: false,
      errorMessage: "",
      successMessage: ""
    };
  },
  methods: {
    async handleRegister() {
      this.errorMessage = "";
      this.successMessage = "";
      this.loading = true;

      try {
        await apiFetch("/api/auth/register/student", {
          method: "POST",
          body: JSON.stringify(this.form)
        });

        this.successMessage = "Registered! Redirecting to login...";

        setTimeout(() => {
          window.location.hash = "/login";
        }, 1200);

      } catch (err) {
        this.errorMessage =
          err.data?.error || "Registration failed.";
      } finally {
        this.loading = false;
      }
    }
  }
};
</script>
