// sets the minimum date to current day
// new Date() - creates JS Date object w current date
// .toISOString() - converts to format 2025-12-29T14:30.45.123Z
// .split('T')[0] - splits by 'T' and takes first part -> 2025-12-29
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