export async function apiFetch(url, options = {}) {
    const token = localStorage.getItem("access_token");
    const headers = { "Content-Type": "application/json", ...(options.headers || {}) };
    if (token) headers["Authorization"] = "Bearer " + token;

    const res = await fetch(url, { ...options, headers });
    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
        const error = new Error(data.error || "Request failed");
        error.data = data;
        throw error;
    }
    return data;
}

export function logout() {
    localStorage.clear();
    window.location.hash = "/login";
}