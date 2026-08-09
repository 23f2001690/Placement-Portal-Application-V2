import { apiFetch } from "/src/api.js";

export default {
    data() {
        return { email: "", password: "", loading: false, errorMessage: "", showError: false };
    },
    methods: {
        async handleLogin() {
            this.hideError();
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
                this.flashError(err.data?.error || "Login failed. Please try again.");
            } finally {
                this.loading = false;
            }
        },
        flashError(message) {
            this.errorMessage = message;
            this.showError = true;
            clearTimeout(this._flashTimer);
            this._flashTimer = setTimeout(() => this.hideError(), 4000);
        },
        hideError() {
            this.showError = false;
        },
    },
    template: `
        <div class="d-flex justify-content-center align-items-center vh-100 bg-light">

          <div v-if="showError"
               class="alert alert-danger alert-dismissible fade show position-fixed top-0 start-50 translate-middle-x mt-3"
               style="z-index: 1080; min-width: 320px;" role="alert">
            {{ errorMessage }}
            <button type="button" class="btn-close" @click="hideError"></button>
          </div>

          <div class="card shadow-sm p-4" style="width: 380px;">
            <h4 class="mb-3 text-center">Placement Portal Login</h4>

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