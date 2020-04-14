let servingsCounter = parseInt(document.getElementById("servings").innerText);
let ingredientServings = Array.from(document.getElementsByClassName("serving-span"));
const defaultRecipeServings = servingsCounter;
const defaultIngredientServings = ingredientServings.map(elem => parseFloat(elem.innerText));

function decrServings() {
    if (servingsCounter > 1) {
        addToServings(-1)
    }
}

function incrServings() {
    addToServings(1)
}

function addToServings(num) {
    servingsCounter = servingsCounter + num;
    let ratio = servingsCounter / defaultRecipeServings;

    document.getElementById("servings").innerText = servingsCounter;
    for (let i = 0; i < ingredientServings.length; i++) {
        amount = (defaultIngredientServings[i] * ratio).toFixed(1) / 1;
        console.log(amount + ": " + isNaN(amount));
        ingredientServings[i].innerText = isNaN(amount) ? "": amount;
    }
}
addToServings(0);