const imageInput = document.getElementById('imageInput');
const imageForm = document.getElementById('imageForm');
const preview = document.getElementById('preview');




//const ws = new WebSocket('ws://localhost:5001/ws');
const ws = new WebSocket('wss://pharmacompare-3a46.onrender.com/ws');

//htps://pharmacompare-3a46.onrender.com

let localClientId = null;
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
            alert("cleint id is: "+ client_id_v)

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
