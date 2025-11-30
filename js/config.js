// Correct API base resolution:
// - When running locally (localhost:8000 or file://), use http://127.0.0.1:5000
// - When running on GitHub Pages, STILL use http://127.0.0.1:5000
// because the backend is local during the demo.

const API_BASE = "http://127.0.0.1:5000";
