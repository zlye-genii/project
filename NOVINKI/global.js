const toggleButton = document.getElementById('toggleButton');
toggleButton.addEventListener('click', function () {
    if (toggleButton.onclick) {
        toggleButton.style.backgroundColor = 'red';
    } else {
        toggleButton.style.backgroundColor = 'gray';
    }
});