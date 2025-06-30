const imageInput = document.getElementById('imageInput');
const imageForm = document.getElementById('imageForm');
const preview = document.getElementById('preview');




const ws = new WebSocket('ws://localhost:5001/ws');

// 3. RECEIVING messages from the server
// This is the most important part for you: reacting to server data
ws.onmessage = function(event) {
    const serverMessage = event.data;
    alert(serverMessage)
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
        alert(serverJson['type'])
        if (serverJson['type'] === 'client_id') {
            alert(serverJson['data'])
            const client_id_v = serverJson['data']
            alert(client_id_v)
            fetch('/client_id_set', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ client_id: client_id_v })
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
