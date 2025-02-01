document.addEventListener('DOMContentLoaded', function() {
    const minFrequencyInput = document.getElementById('min-frequency');
    const entityType1Select = document.getElementById('entity-type-1');
    const entityType2Select = document.getElementById('entity-type-2');

    // Set initial values based on query parameters (already populated by the backend)
    const urlParams = new URLSearchParams(window.location.search);
    const minFrequency = urlParams.get('min_frequency') || minFrequencyInput.value;
    const entityType1 = urlParams.get('entity_type_1') || entityType1Select.value;
    const entityType2 = urlParams.get('entity_type_2') || entityType2Select.value;

    // Set the initial values
    minFrequencyInput.value = minFrequency;
    entityType1Select.value = entityType1;
    entityType2Select.value = entityType2;

    // Listen for changes in the filters
    minFrequencyInput.addEventListener('input', updateFilters);
    entityType1Select.addEventListener('change', updateFilters);
    entityType2Select.addEventListener('change', updateFilters);

    function updateFilters() {
        const minFrequency = minFrequencyInput.value;
        const entityType1 = entityType1Select.value;
        const entityType2 = entityType2Select.value;

        // Construct the query parameters
        let queryParams = [];
        if (minFrequency) {
            queryParams.push(`min_frequency=${minFrequency}`);
        }
        if (entityType1 !== 'All Types') {
            queryParams.push(`entity_type_1=${entityType1}`);
        }
        if (entityType2 !== 'All Types') {
            queryParams.push(`entity_type_2=${entityType2}`);
        }

        // Reload the page with the updated filters
        let queryString = queryParams.join('&');
        if (queryString) {
            window.location.search = '?' + queryString;
        } else {
            window.location.search = '';  // Reset to default state without filters
        }
    }
});


