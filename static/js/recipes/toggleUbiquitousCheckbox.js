let ubiquitousCheckboxContainer = document.getElementById("ubiq-checkbox-container");
let bestMatchOption = document.getElementById("best-match-option");

function radioToggle(event) {
    if (event.target.value === 'True') {
        ubiquitousCheckboxContainer.style.display = 'block';
        bestMatchOption.remove()
    } else {
        ubiquitousCheckboxContainer.style.display = 'none';
    }
}