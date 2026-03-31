// Utility helpers for exporting lead data

/**
 * Downloads the current in-memory leads array as a JSON file.
 * @param {Array} leads - The leads array from React state
 */
function exportJSON(leads) {
    if (!leads || leads.length === 0) return;
    const dataStr = "data:text/json;charset=utf-8," + encodeURIComponent(JSON.stringify(leads, null, 2));
    const anchor = document.createElement("a");
    anchor.setAttribute("href", dataStr);
    anchor.setAttribute("download", "leads.json");
    document.body.appendChild(anchor);
    anchor.click();
    anchor.remove();
}

/**
 * Fetches leads CSV from the backend and triggers a browser download.
 * Returns { success: true } or throws on error.
 */
async function handleDownloadCSV() {
    const response = await apiClient({
        url: "/api/download-csv",
        method: "GET",
        responseType: "blob",
    });

    const url = window.URL.createObjectURL(new Blob([response.data]));
    const link = document.createElement("a");
    link.href = url;
    link.setAttribute("download", "leads_export.csv");
    document.body.appendChild(link);
    link.click();
    link.remove();

    return { success: true };
}
