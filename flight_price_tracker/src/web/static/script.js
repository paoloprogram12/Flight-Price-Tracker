// sets the minimum date to current day
const today = new Date().toISOString().split('T')[0];
document.getElementById('departure_date').setAttribute('min', today);

// Updates the return date minimum when departure changes
document.getElementById('departure_date').addEventListener('change', function() {
    document.getElementById('return_date').setAttribute('min', this.value);
});

// handles trip type changes
const tripTypeInputs = document.querySelectorAll('input[name="trip_type"]');
const returnDateGroup = document.getElementById('return_date_group');

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