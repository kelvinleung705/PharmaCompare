const imageInput = document.getElementById('imageInput');
const imageForm = document.getElementById('imageForm');
const preview = document.getElementById('preview');

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
