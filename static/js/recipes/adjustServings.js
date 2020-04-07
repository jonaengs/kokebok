let servingsCounter = parseInt(document.getElementById("servings").innerText);
let ingredientServings = Array.from(document.getElementsByClassName("serving-span"));

function decrServings() {
    if (servingsCounter > 1) {
        addToServings(-1)
    }
}

function incrServings() {
    addToServings(1)
}

function addToServings(num) {
    let prevCounter = servingsCounter;
    servingsCounter = servingsCounter + num;
    let ratio = servingsCounter / prevCounter;

    document.getElementById("servings").innerText = servingsCounter;
    ingredientServings.forEach(elem => elem.innerText = parseInt(elem.innerText) * ratio);
}