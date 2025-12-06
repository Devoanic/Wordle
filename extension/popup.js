// Popup script for Wordle Solver extension

document.addEventListener("DOMContentLoaded", () => {
  const statusDiv = document.getElementById("status");
  const refreshBtn = document.getElementById("refresh");

  async function checkConnection() {
    try {
      const response = await fetch("http://localhost:5000/api/starting-words");
      if (response.ok) {
        statusDiv.textContent = "✓ Connected to server";
        statusDiv.className = "status connected";
      } else {
        throw new Error("Server not responding");
      }
    } catch (error) {
      statusDiv.textContent = "✗ Server not running";
      statusDiv.className = "status disconnected";
    }
  }

  refreshBtn.addEventListener("click", checkConnection);

  // Check on load
  checkConnection();

  // Auto-check every 5 seconds
  setInterval(checkConnection, 5000);
});

