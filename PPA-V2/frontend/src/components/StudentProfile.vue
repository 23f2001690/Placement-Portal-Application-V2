import { apiFetch } from "/src/api.js";

export default {
    data() {
        return { profile: null, loading: true, saving: false, uploading: false, message: "", resumeFile: null };
    },
    async mounted() {
        this.profile = await apiFetch("/api/student/profile");
        this.loading = false;
    },
    methods: {
        async saveProfile() {
            this.saving = true;
            this.message = "";
            try {
                const data = await apiFetch("/api/student/profile", {
                    method: "PUT",
                    body: JSON.stringify(this.profile),
                });
                this.profile = data.profile;
                this.message = "Profile updated.";
            } catch (err) {
                this.message = err.data?.error || "Could not update profile.";
            } finally {
                this.saving = false;
            }
        },
        onFileChange(event) {
            this.resumeFile = event.target.files[0] || null;
        },
        async uploadResume() {
            if (!this.resumeFile) return;
            this.uploading = true;
            const formData = new FormData();
            formData.append("resume", this.resumeFile);
            try {
                await apiFetch("/api/student/resume", { method: "POST", body: formData });
                this.profile = await apiFetch("/api/student/profile");
                this.resumeFile = null;
                this.message = "Resume uploaded.";
            } catch (err) {
                this.message = err.data?.error || "Could not upload resume.";
            } finally {
                this.uploading = false;
            }
        },
    },
    template: `
        <div>
          <p v-if="loading">Loading profile...</p>
          <div v-else class="card p-3">
            <div v-if="message" class="alert alert-info py-2">{{ message }}</div>

            <div class="row">
              <div class="col mb-2">
                <label class="form-label">Full Name</label>
                <input v-model="profile.full_name" class="form-control" />
              </div>
              <div class="col mb-2">
                <label class="form-label">Branch</label>
                <input v-model="profile.branch" class="form-control" />
              </div>
            </div>
            <div class="row">
              <div class="col mb-2">
                <label class="form-label">Year of Study</label>
                <input v-model.number="profile.year_of_study" type="number" class="form-control" />
              </div>
              <div class="col mb-2">
                <label class="form-label">CGPA</label>
                <input v-model.number="profile.cgpa" type="number" step="0.01" class="form-control" />
              </div>
            </div>
            <div class="mb-2">
              <label class="form-label">Skills (comma separated)</label>
              <input v-model="profile.skills" class="form-control" />
            </div>
            <div class="mb-3">
              <label class="form-label">Experience</label>
              <textarea v-model="profile.experience" class="form-control" rows="3" placeholder="Internships, projects, etc."></textarea>
            </div>
            <button class="btn btn-primary" :disabled="saving" @click="saveProfile">
              {{ saving ? "Saving..." : "Save Profile" }}
            </button>

            <hr />

            <h6>Resume</h6>
            <p v-if="profile.resume_path" class="text-muted">Current file: {{ profile.resume_path }}</p>
            <p v-else class="text-muted">No resume uploaded yet.</p>
            <input type="file" class="form-control mb-2" @change="onFileChange" />
            <button class="btn btn-outline-primary" :disabled="!resumeFile || uploading" @click="uploadResume">
              {{ uploading ? "Uploading..." : "Upload Resume" }}
            </button>
          </div>
        </div>
    `,
};