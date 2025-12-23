const imageInput = document.getElementById('imageInput');
const imageForm = document.getElementById('imageForm');
const preview = document.getElementById('preview');




//const ws = new WebSocket('ws://localhost:5001/ws');
const ws = new WebSocket('wss://pharmacompare-3a46.onrender.com/ws');

//htps://pharmacompare-3a46.onrender.com

let localClientId = null;

let pharmacyMarkers = [];
let map;

/*
(function() {
 */
// 3. RECEIVING messages from the server
// This is the most important part for you: reacting to server data
ws.onmessage = function(event) {
    const serverMessage = event.data;
    //alert(serverMessage)
    let serverJson;
    try {
        serverJson = JSON.parse(serverMessage);
    } catch (e) {
        console.error("Failed to parse server message as JSON:", serverMessage, e);
        return;  // Stop if the message isn't valid JSON
    }
    console.log("Message received from server: " + serverMessage);
    const keys = Object.keys(serverJson);
    if (serverJson.hasOwnProperty('type')) {
        console.log("The 'type' key exists!");
        //alert(serverJson['type'])
        if (serverJson['type'] === 'client_id') {
            //alert(serverJson['data'])
            localClientId = serverJson['data']
            const client_id_v = serverJson['data']
            alert("client id is: "+ client_id_v)

        } else if (serverJson['type'] === 'update') {
            alert("Update: "+ serverJson['data'])
        }
    }

    // You can do anything you want with the message here!
};



imageInput.addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (!file) {
        preview.style.display = 'none';
        preview.src = '';
        return;
    }
    const reader = new FileReader();
    reader.onload = function(e) {
        preview.src = e.target.result;
        preview.style.display = 'block';
        document.getElementById('imageBase64Input').value = e.target.result;
    }
    reader.readAsDataURL(file);
});


imageForm.addEventListener('submit', async function(event) {
    event.preventDefault(); // Prevent traditional form submission

    const file = imageInput.files[0];

    if (!file) {
        alert("Please select an image first.");
        return;
    }
    if (!localClientId) {
        alert("Cannot upload: Client ID not yet received from server. Please wait.");
        return;
    }

    // THE FIX: Use FormData to properly package the file for upload.
    // This is much better than Base64 for sending files.
    const formData = new FormData();
    formData.append("file", file);

    // THE CRITICAL FIX: Build the correct upload URL using our unique ID.
    // This tells the FastAPI server who we are.
    //const uploadUrl = `http://localhost:5001/upload/${localClientId}`;

    const uploadUrl = `https://pharmacompare-3a46.onrender.com/upload/${localClientId}`;

    console.log(`Uploading file to: ${uploadUrl}`);
    alert(`Uploading file to: ${uploadUrl}`);

    try {
        // Send the file DIRECTLY to the FastAPI server.
        const response = await fetch(uploadUrl, {
            method: 'POST',
            body: formData
            // NOTE: Do not set Content-Type header when using FormData with fetch.
            // The browser sets it correctly automatically.
        });

        const result = await response.json();

        if (response.status === 202) {
            // The server accepted our file. Now we just wait for the WebSocket message.
            console.log(result.message);
            alert("Upload accepted! Waiting for processing update via WebSocket.");
        } else {
            // The server rejected the upload immediately.
            console.error("Upload failed:", result.message);
            alert(`Upload failed: ${result.message}`);
        }
    } catch (error) {
        console.error("An error occurred during upload:", error);
        alert("An error occurred during upload. Check the console.   code 1");
    }
});






// ==========================================================
// 4. GOOGLE MAP LOGIC
// ==========================================================

/**
 * THIS IS THE ENTRY POINT FOR THE MAP.
 * It's called by the Google Maps script tag in the HTML.
 * It MUST be in the global scope.
 */


function initMap() {
    const initialCenter = { lat: 43.6584, lng: -79.3883 };
    map = new google.maps.Map(document.getElementById("map"), {
        zoom: 10,
        center: initialCenter,
    });
    loadAndDisplayPharmacies();
}

/**
 * Creates the HTML content for a pharmacy's InfoWindow.
 */
function createPharmacyInfoWindowContent(pharmacy) {
    const feeText = pharmacy.processing_fee
        ? `<b>Processing Fee: $${pharmacy.processing_fee.toFixed(2)}</b>`
        : "Processing fee not available.";

    return `
        <div class="infowindow-content">
            <h4>${pharmacy.name}</h4>
            <p>${pharmacy.address}</p>
            <hr>
            <p>${feeText}</p>
        </div>
    `;
}

/**
 * Fetches all pharmacy data from an API and adds markers to the map.
 */
async function loadAndDisplayPharmacies() {
    try {
        // NOTE: Make sure your Flask server is running and accessible at this URL.
        const response = await fetch('http://127.0.0.1:5000/api/pharmacies');
        const allPharmacies = await response.json();

        if (allPharmacies.length === 0) {
            console.warn("No pharmacies found.");
            return;
        }

        pharmacyMarkers.forEach(marker => marker.setMap(null));
        pharmacyMarkers = [];

        const infowindow = new google.maps.InfoWindow();

        allPharmacies.forEach(pharmacy => {
            const position = { lat: pharmacy.lat, lng: pharmacy.lng };
            const marker = new google.maps.Marker({
                position: position,
                map: map,
                title: pharmacy.name,
            });

            marker.addListener('click', () => {
                const content = createPharmacyInfoWindowContent(pharmacy);
                infowindow.setContent(content);
                infowindow.open(map, marker);
            });

            pharmacyMarkers.push(marker);
        });
    } catch (error) {
        console.error("Failed to load pharmacy data:", error);
        alert("Could not load pharmacy locations. Please ensure the data server is running and accessible.");
    }
}


/*
imageForm.addEventListener('submit', function(event) {
    event.preventDefault();  // Prevent traditional form submission

    const imageBase64 = document.getElementById('imageBase64Input').value;
    if (!imageBase64) {
        alert("Please select an image first");
        return;
    }

    fetch('/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ image_base64: imageBase64 })
    })
    .then(response => response.text())
    .then(result => {
        console.log("Server response:", result);
        alert(result)
        //alert("Image submitted successfully!");
    })
    .catch(error => {
        console.error("Error submitting image:", error);
        alert("Submission failed.");
    });
});

 */

/*
})(); // The function is called immediately.
*/
