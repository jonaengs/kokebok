let ubiquitousCheckboxContainer = document.getElementById("ubiq-checkbox-container");

function toggleUbiq(event) {
    if (event.target.value === 'True') {
        ubiquitousCheckboxContainer.style.display = 'block';
    } else if (event.target.value === 'False') {
        ubiquitousCheckboxContainer.style.display = 'none';
    } else {
        console.log("error when toggling ubiq checkbox")
    }
}