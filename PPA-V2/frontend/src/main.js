import Login from "/src/components/Login.vue";
import RegisterStudent from "/src/components/RegisterStudent.vue";
import RegisterCompany from "/src/components/RegisterCompany.vue";
import AdminDashboard from "/src/components/AdminDashboard.vue";
import CompanyDashboard from "/src/components/CompanyDashboard.vue";
import StudentDashboard from "/src/components/StudentDashboard.vue";

const pages = {
    "/login": Login,
    "/register/student": RegisterStudent,
    "/register/company": RegisterCompany,
    "/admin": AdminDashboard,
    "/company": CompanyDashboard,
    "/student": StudentDashboard,
};

const publicPaths = ["/login", "/register/student", "/register/company"];
const roleHome = { admin: "/admin", company: "/company", student: "/student" };

function rawPath() {
    return window.location.hash.slice(1) || "/login";
}

// blocks logged-out users from dashboards, and blocks a role from another role's dashboard
function guardedPath(path) {
    const token = localStorage.getItem("access_token");
    const role = localStorage.getItem("role");

    if (!publicPaths.includes(path) && !token) return "/login";
    if (Object.values(roleHome).includes(path) && roleHome[role] !== path) {
        return roleHome[role] || "/login";
    }
    return path;
}

const App = {
    data() {
        return { path: guardedPath(rawPath()) };
    },
    computed: {
        activeComponent() {
            return pages[this.path] || Login;
        },
    },
    mounted() {
        window.addEventListener("hashchange", () => {
            this.path = guardedPath(rawPath());
        });
        if ("#" + this.path !== window.location.hash) {
            window.location.hash = this.path;
        }
    },
    watch: {
        path(newPath) {
            if ("#" + newPath !== window.location.hash) {
                window.location.hash = newPath;
            }
        },
    },
    template: `<component :is="activeComponent"></component>`,
};

Vue.createApp(App).mount("#app");