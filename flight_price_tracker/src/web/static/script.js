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
// inputElement - the input field to attach autocomplete to (input field as a parameter)
function setupAutocomplete(inputElement) {
    let currentFocus = -1; // tracks which suggestion is highlighted -1 means nothing, 0 is first item, 1 is second

    // Listen for when user types in the input field
    inputElement.addEventListener('input', function() {
        const inputValue = this.value.toUpperCase(); // convert to uppercase for matching
        closeAllLists(); // close any already open dropdown (doesn't show any suggestions)

        if (!inputValue) { return; } // if the input is empty, don't show any suggestions

        currentFocus = -1; // resets highlighting when new suggestions appear

        // create a div to hold the autocomplete suggestions
        const autocompleteList = document.createElement('div'); // creates a new HTML div element for each suggestion
        autocompleteList.setAttribute('id', this.id + '-autocomplete-list'); // gives it an ID
        autocompleteList.setAttribute('class', 'autocomplete-items'); // adds css class for styling
        this.parentNode.appendChild(autocompleteList); // adds dropdown div as a child of form-group

        // filter airports that match what user typed
        // for each airport object, it checks if it matches airport code, city name, or airport name
        const matches = airports.filter(airport => 
            airport.code.includes(inputValue) ||
            airport.city.toUpperCase().includes(inputValue) ||
            airport.name.toUpperCase().includes(inputValue) ||
            (airport.state && airport.state.toUpperCase().includes(inputValue)) ||
            (airport.country && airport.country.toUpperCase().includes(inputValue))
        );

        // shows the first 5 matches
        matches.slice(0, 5).forEach(airport => {
            const item = document.createElement('div'); // creates div for each suggestion
            item.innerHTML = `
            <div>
            <strong>${airport.code}</strong> - ${airport.city} (${airport.name})
            </div>
            <div class="country">${airport.country}</div>`;
            item.dataset.code = airport.code; // stores airport code in data attribute

            // when user clicks on a suggestion
            item.addEventListener('click', function() { // when user clicks suggestion,
                inputElement.value = this.dataset.code; // fills input with airport code
                closeAllLists(); // closes dropdown
            });

            autocompleteList.appendChild(item); // adds the suggestion item to the dropdown list

        });
    });

    // handles keyboard navigation
    inputElement.addEventListener('keydown', function(e) {
        let list = document.getElementById(this.id + '-autocomplete-list'); // gets the dropdown element
        if (list) {
            let items = list.querySelectorAll(':scope > div');

            if (e.keyCode === 40) { // DOWN arrow
                currentFocus++;
                addActive(items);
                } else if (e.keyCode === 38) { // UP arrow
                    currentFocus--;
                    addActive(items);    
                } else if (e.keyCode === 13) { // ENTER key
                    e.preventDefault(); // stops the form from submitting when you press enter
                    if (currentFocus > -1 && items[currentFocus]) { // if something is highlighted (currentFocus > -1)
                        items[currentFocus].click(); // and if it exists, simulate a click on it and selected the suggestion
                    }
                }
        }
    });

    // highlights the active item
    function addActive(items) {
        if (!items) { return; }
        removeActive(items); // removes highlight from all items
        if (currentFocus >= items.length) { currentFocus = 0; } // if we went past the last item, loop back to first
        if (currentFocus < 0) { currentFocus = items.length - 1; } // if we went before first item, loop to the last
        items[currentFocus].classList.add('autocomplete-active'); // adds the CSS class to highlight the item
    }

    // removes highlight from all items
    function removeActive(items) { // loops through suggestion items
        for (let i = 0; i < items.length; i++) { // removes highlight class from each one
            items[i].classList.remove('autocomplete-active');
        }
    }

    // close all autocomplete dropdowns
    function closeAllLists(except) {
        const lists = document.getElementsByClassName('autocomplete-items');
        for (let i = 0; i < lists.length; i++) {
            if (except !== lists[i] && except !== inputElement) {
                lists[i].parentNode.removeChild(lists[i]); // .removeChild() deletes it from the DOM
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

// setup autocomplete for results page search inputs (if they exist)
const resultsOrigin = document.getElementById('results-origin');
const resultsDestination = document.getElementById('results-destination');

if (resultsOrigin && resultsDestination) {
    // wait for airport data to load, then setup autocomplete
    const checkAirportsLoaded = setInterval(() => {
        if (airports.length > 0) {
            setupAutocomplete(resultsOrigin);
            setupAutocomplete(resultsDestination);
            clearInterval(checkAirportsLoaded);
        }
    }, 100);
}