// sets the minimum date to current day
// new Date() - creates JS Date object w current date
// .toISOString() - converts to format 2025-12-29T14:30.45.123Z
// .split('T')[0] - splits by 'T' and takes first part -> 2025-12-29

// stores airport data
let airports = [];

// fetches airport data from JSON file
// runs when page loads and gets airport data
fetch('/static/airports.json')
    .then(response => response.json()) // convert response to JSON
    .then(data => {
        airports = data; // store the data in our global variable
        // setup autocomplete after data is loaded
        setupAutocomplete(document.getElementById('origin'));
        setupAutocomplete(document.getElementById('destination'));
    })
    .catch(error => console.error('Error loading airport data: ', error));

// autocomplete function
// inputElement - the input field to attach autocomplete to
function setupAutocomplete(inputElement) {
    let currentFocus = -1; // tracks which suggestion is highlighted

    // Listen for when user types in the input field
    inputElement.addEventListener('input', function() {
        const inputValue = this.value.toUpperCase(); // convert to uppercase for matching
        closeAllLists(); // close any already open dropdown

        if (!inputValue) { return; } // if the input is empty, don't show any suggestions

        currentFocus = -1;

        // create a div to hold the autocomplete suggestions
        const autocompleteList = document.createElement('div');
        autocompleteList.setAttribute('id', this.id + '-autocomplete-list');
        autocompleteList.setAttribute('class', 'autocomplete-items');
        this.parentNode.appendChild(autocompleteList);

        // filter airports that match what user typed
        const matches = airports.filter(airport => 
            airport.code.includes(inputValue) ||
            airport.city.toUpperCase().includes(inputValue) ||
            airport.name.toUpperCase().includes(inputValue)
        );

        // shows the first 5 matches
        matches.slice(0, 5).forEach(airport => {
            const item = document.createElement('div');
            item.innerHTML = `<strong>${airport.code}</strong> ~ ${airport.city} (${airport.name})`;
            item.dataset.code = airport.code;

            // when user clicks on a suggestion
            item.addEventListener('click', function() {
                inputElement.value = this.dataset.code;
                closeAllLists();
            });

            autocompleteList.appendChild(item);

        });
    });

    // handles keyboard navigation
    inputElement.addEventListener('keydown', function(e) {
        let list = document.getElementById(this.id + '-autocomplete-list');
        if (list) {
            let items = list.getElementsByTagName('div');

            if (e.keyCode === 40) { // DOWN arrow
                currentFocus++;
                addActive(items);
                } else if (e.keyCode === 38) { // UP arrow
                    currentFocus--;
                    addActive(items);    
                } else if (e.keyCode === 13) { // ENTER key
                    e.preventDefault();
                    if (currentFocus > -1 && items[currentFocus]) {
                        items[currentFocus].click();
                    }
                }
        }
    });

    // highlights the active item
    function addActive(items) {
        if (!items) { return; }
        removeActive(items);
        if (currentFocus >= items.length) { currentFocus = 0; }
        if (currentFocus < 0) { currentFocus = items.length - 1; }
        items[currentFocus].classList.add('autocomplete-active');
    }

    // removes highlight from all items
    function removeActive(items) {
        for (let i = 0; i < items.length; i++) {
            items[i].classList.remove('autocomplete-active');
        }
    }

    // close all autocomplete dropdowns
    function closeAllLists(except) {
        const lists = document.getElementsByClassName('autocomplete-items');
        for (let i = 0; i < lists.length; i++) {
            if (except !== lists[i] && except !== inputElement) {
                lists[i].parentNode.removeChild(lists[i]);
            }
        }
    }

    // close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        closeAllLists(e.target);
    });
}

const today = new Date().toISOString().split('T')[0];
document.getElementById('departure_date').setAttribute('min', today); // sets min attribute to todays date

// Updates the return date minimum when departure changes
// runs code when departure date changes
// sets return date min to departure date
document.getElementById('departure_date').addEventListener('change', function() {
    document.getElementById('return_date').setAttribute('min', this.value);
});

// handles trip type changes
// querySelectorAll('input[name="trip_type"]') - finds all input elements with trip_type and returns a NodeList
const tripTypeInputs = document.querySelectorAll('input[name="trip_type"]');
const returnDateGroup = document.getElementById('return_date_group');

// input - represents each radio button
// adds a listener to each radio button
// runs the function whenever radio button is clicked
tripTypeInputs.forEach(input => {
    input.addEventListener('change', function() {
        if (this.value === 'one-way') {
            returnDateGroup.disabled = true;
            returnDateGroup.required = false;
            returnDateGroup.value = '';
            returnDateGroup.style.display = 'none';
            
        } else {
            returnDateGroup.disabled = false;
            returnDateGroup.required = true;
            returnDateGroup.style.display = 'block';
        }
    });
});