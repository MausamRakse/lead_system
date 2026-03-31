// API base URL — set window.API_BASE_URL in index.html for easy deployment config
const API_BASE = window.API_BASE_URL || "http://127.0.0.1:8000";

const apiClient = axios.create({
    baseURL: API_BASE,
});
