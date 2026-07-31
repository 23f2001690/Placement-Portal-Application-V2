import { apiFetch } from "/src/api.js";

export default {
    data() {
        return { email: "", password: "", loading: false, errorMessage: "" };
    },
    methods: {
        async handleLogin() {
            this.errorMessage = "";
            this.loading = true;
            try {
                const data = await apiFetch("/api/auth/login", {
                    method: "POST",
                    body: JSON.stringify({ email: this.email, password: this.password }),
                });
                localStorage.setItem("access_token", data.access_token);
                localStorage.setItem("role", data.role);
                window.location.hash = "/" + data.role;
            } catch (err) {
                this.errorMessage = err.data?.error || "Login failed. Please try again.";
            } finally {
                this.loading = false;
            }
        },
    },
    template: `
        <div class="d-flex justify-content-center align-items-center vh-100 bg-light">
          <div class="card shadow-sm p-4" style="width: 380px;">
            <h4 class="mb-3 text-center">Placement Portal Login</h4>
            <div v-if="errorMessage" class="alert alert-danger py-2">{{ errorMessage }}</div>
            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input v-model="email" type="email" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Password</label>
                <input v-model="password" type="password" class="form-control" required />
              </div>
              <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                {{ loading ? "Logging in..." : "Login" }}
              </button>
            </form>
            <hr />
            <p class="text-center mb-1">Don't have an account?</p>
            <div class="d-flex gap-2">
              <a href="#/register/student" class="btn btn-outline-secondary w-50">Student</a>
              <a href="#/register/company" class="btn btn-outline-secondary w-50">Company</a>
            </div>
          </div>
        </div>
    `,
};
