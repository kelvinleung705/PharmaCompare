document.addEventListener('DOMContentLoaded', function () {
    const input = document.querySelector('input[type="file"]');
    const preview = document.getElementById('preview');

    input.addEventListener('change', function (event) {
        const file = event.target.files[0];
        if (!file) return;

        const reader = new FileReader();
        reader.onload = function () {
            preview.src = reader.result;
            preview.style.display = 'block';
        };
        reader.readAsDataURL(file);
    });
});
