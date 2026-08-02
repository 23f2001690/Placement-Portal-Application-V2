export async function apiFetch(url, options = {}) {
    const token = localStorage.getItem("access_token");
    const isFormData = options.body instanceof FormData;
    const headers = { ...(isFormData ? {} : { "Content-Type": "application/json" }), ...(options.headers || {}) };
    if (token) headers["Authorization"] = "Bearer " + token;

    const res = await fetch(url, { ...options, headers });
    const contentType = res.headers.get("content-type") || "";
    const data = contentType.includes("application/json") ? await res.json().catch(() => ({})) : null;

    if (!res.ok) {
        const error = new Error((data && data.error) || "Request failed");
        error.data = data;
        throw error;
    }
    return data;
}

export async function apiDownload(url, fallbackName) {
    const token = localStorage.getItem("access_token");
    const res = await fetch(url, { headers: token ? { Authorization: "Bearer " + token } : {} });

    if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.error || "Download failed");
    }

    const disposition = res.headers.get("content-disposition") || "";
    const match = disposition.match(/filename=([^;]+)/);
    const filename = match ? match[1].trim() : (fallbackName || "download");

    const blob = await res.blob();
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(link.href);
}

export function logout() {
    localStorage.clear();
    window.location.hash = "/login";
}