// API base URL — set window.API_BASE_URL in index.html for easy deployment config.
// Empty string means same-origin (correct for Render unified deployment).
const API_BASE = window.API_BASE_URL || "";

const apiClient = axios.create({
    baseURL: API_BASE,
});
