import { apiFetch } from "/src/api.js";

export default {
    data() {
        return {
            form: { company_name: "", email: "", password: "", industry: "", location: "", website: "", hr_contact: "" },
            loading: false,
            errorMessage: "",
            successMessage: "",
        };
    },
    methods: {
        async handleRegister() {
            this.errorMessage = "";
            this.successMessage = "";
            this.loading = true;
            try {
                await apiFetch("/api/auth/register/company", {
                    method: "POST",
                    body: JSON.stringify(this.form),
                });
                this.successMessage = "Registered! Pending admin approval. Redirecting to login...";
                setTimeout(() => { window.location.hash = "/login"; }, 1500);
            } catch (err) {
                this.errorMessage = err.data?.error || "Registration failed.";
            } finally {
                this.loading = false;
            }
        },
    },
    template: `
        <div class="d-flex justify-content-center align-items-center vh-100 bg-light">
          <div class="card shadow-sm p-4" style="width: 420px;">
            <h4 class="mb-3 text-center">Company Registration</h4>
            <div v-if="errorMessage" class="alert alert-danger py-2">{{ errorMessage }}</div>
            <div v-if="successMessage" class="alert alert-success py-2">{{ successMessage }}</div>
            <form @submit.prevent="handleRegister">
              <div class="mb-2">
                <label class="form-label">Company Name</label>
                <input v-model="form.company_name" class="form-control" required />
              </div>
              <div class="mb-2">
                <label class="form-label">Email</label>
                <input v-model="form.email" type="email" class="form-control" required />
              </div>
              <div class="mb-2">
                <label class="form-label">Password</label>
                <input v-model="form.password" type="password" class="form-control" required />
              </div>
              <div class="mb-2">
                <label class="form-label">Industry</label>
                <input v-model="form.industry" class="form-control" />
              </div>
              <div class="mb-2">
                <label class="form-label">Location</label>
                <input v-model="form.location" class="form-control" />
              </div>
              <div class="mb-2">
                <label class="form-label">Website</label>
                <input v-model="form.website" class="form-control" />
              </div>
              <div class="mb-3">
                <label class="form-label">HR Contact</label>
                <input v-model="form.hr_contact" class="form-control" />
              </div>
              <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                {{ loading ? "Registering..." : "Register" }}
              </button>
            </form>
            <p class="text-center mt-3 mb-0">Already have an account? <a href="#/login">Login</a></p>
          </div>
        </div>
    `,
};