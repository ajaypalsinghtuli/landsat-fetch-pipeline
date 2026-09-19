// Initialize the map (centered globally)
const map = L.map('map').setView([20, 0], 3);

// Add OpenStreetMap base layer
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
}).addTo(map);

// Add drawing controls
const drawnItems = new L.FeatureGroup();
map.addLayer(drawnItems);

const drawControl = new L.Control.Draw({
    draw: {
        polygon: true,
        rectangle: true,
        polyline: false,
        circle: false,
        circlemarker: false,
        marker: false
    },
    edit: {
        featureGroup: drawnItems
    }
});
map.addControl(drawControl);

let userGeoJSON = null;
const submitBtn = document.getElementById('submit-btn');

// Capture the drawn shape
map.on(L.Draw.Event.CREATED, function (event) {
    const layer = event.layer;
    drawnItems.clearLayers(); // Only allow one shape at a time
    drawnItems.addLayer(layer);
    
    // Convert drawing to GeoJSON
    userGeoJSON = layer.toGeoJSON();
    
    // Enable the submit button
    submitBtn.disabled = false;
    submitBtn.innerText = "Submit Job";
});

// Handle form submission
document.getElementById('job-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    if (!userGeoJSON) return;

    const email = document.getElementById('email').value;
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;

    submitBtn.disabled = true;
    submitBtn.innerText = "Submitting...";

    try {
        const response = await fetch('/api/submit-job', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                email: email,
                start_date: startDate,
                end_date: endDate,
                geojson: userGeoJSON
            })
        });

        const data = await response.json();
        if (response.ok) {
            document.getElementById('status-panel').classList.remove('hidden');
            document.getElementById('task-id').innerText = data.task_id;
            startPolling(data.task_id);
        } else {
            alert('Error: ' + data.error);
            submitBtn.disabled = false;
            submitBtn.innerText = "Submit Job";
        }
    } catch (error) {
        console.error('Submission failed:', error);
    }
});

// Poll the server for job status updates
function startPolling(taskId) {
    const statusElement = document.getElementById('task-status');
    
    const intervalId = setInterval(async () => {
        try {
            const response = await fetch(`/api/job-status/${taskId}`);
            const data = await response.json();
            
            if (response.ok) {
                statusElement.innerText = data.status;
                
                // Stop polling if completed or failed
                if (data.status === 'Completed' || data.status === 'Failed') {
                    clearInterval(intervalId);
                    submitBtn.disabled = false;
                    submitBtn.innerText = "Submit New Job";
                    drawnItems.clearLayers();
                    userGeoJSON = null;
                }
            }
        } catch (error) {
            console.error('Polling failed:', error);
        }
    }, 3000); // Check every 3 seconds
}