let ingredient_search = document.getElementById("ingredient-search");
let all_ingredients = Array.from(document.getElementById("ingredients").children);
let _selected_ingredients = [];  // internal list, used to keep track of ingredients selected from search bar

function append_ingredient_to_list() {
    let ingredient = ingredient_search.value;
    _selected_ingredients.push(ingredient);
    all_ingredients.find(elem => elem.value === ingredient).remove();

    add_to_selected_ingredients(ingredient);
    ingredient_search.value = "";
}

function add_to_selected_ingredients(ingredient) {
    let ingredient_tag_elem = '<p class="field" id="' + ingredient + '-select-p">' +
        '<span class="tag is-primary is-medium"><span class=selected_ingredient_span>' + ingredient + '</span>' +
        '<button class="delete is-small" onclick="make_ingredient_searchable(event)"></button></span></p>';
    document.getElementById("selected-ingredients-container").insertAdjacentHTML('beforeend', ingredient_tag_elem);
}

function set_ingredients(e) {
    // Run on form submit. Sets search bar value to equal all the selected ingredients
    ingredient_search.value = _selected_ingredients.join(",");
}

function make_ingredient_searchable(event) {
    // Run when selected ingredient is removed (X clicked). Removes the html and makes the ingredient searchable again
    let ingredient_name = event.target.previousSibling.innerText;
    let ingredient_p = document.getElementById(ingredient_name + "-select-p");
    ingredient_p.remove();
    _selected_ingredients = _selected_ingredients.filter(ingr => ingr !== ingredient_name);
    let ingredient_option = all_ingredients.find(ingr => ingr.value === ingredient_name);
    document.getElementById("ingredients").appendChild(ingredient_option);
}