// Auto-detect backend API location
const API_BASE = (() => {
    if (window.location.origin.includes("localhost:8000")) {
        return "http://127.0.0.1:5000";
    }
    return "https://rowannoel.github.io/cs582FinalProject";
})();