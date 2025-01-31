// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function () {
    // Initialize the dashboard
    initializeDashboard();

    // Add event listeners for filters
    setupFilterListeners();
});

// Main dashboard initialization
function initializeDashboard() {
    try {
        // Get the charts data from the data attribute
        const chartsContainer = document.getElementById('chartsData');
        if (!chartsContainer) {
            throw new Error('Charts data container not found');
        }

        const chartDataAttr = chartsContainer.getAttribute('data-charts');
        if (!chartDataAttr) {
            throw new Error('No chart data found');
        }

        const chartData = JSON.parse(chartDataAttr);

        // Create all charts
        createCharts(chartData);
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        // Display error message to user
        document.querySelectorAll('.chart').forEach(chart => {
            chart.innerHTML = '<p class="error">Error loading chart data</p>';
        });
    }
}

// Create all charts
function createCharts(chartData) {
    // Configure default layout options
    const layoutDefaults = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: {
            family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        },
        margin: { t: 30, r: 20, b: 40, l: 100 },
        height: 400
    };

    // Create Top Entities chart
    if (chartData.top_entities) {
        Plotly.newPlot('topEntities',
            JSON.parse(chartData.top_entities),
            Object.assign({}, layoutDefaults, {
                xaxis: { gridcolor: '#eee' },
                yaxis: { gridcolor: '#eee' }
            })
        );
    }

    // Create Entity Distribution chart
    if (chartData.entity_dist) {
        Plotly.newPlot('entityDist',
            JSON.parse(chartData.entity_dist),
            Object.assign({}, layoutDefaults)
        );
    }
}

// Handle window resize for responsive charts
window.addEventListener('resize', function () {
    const charts = document.querySelectorAll('.chart');
    charts.forEach(chart => {
        Plotly.Plots.resize(chart);
    });
});

// Setup filter listeners
function setupFilterListeners() {
    const entityTypeCheckboxes = document.querySelectorAll('input[name="entityType"]');
    const topEntitiesInput = document.querySelector('input[data-filter="mentions"]');
    const filterForm = document.getElementById('filterForm');

    if (entityTypeCheckboxes && topEntitiesInput) {
        // Add listener for "All Types" checkbox
        const allTypesCheckbox = document.querySelector('input[value="All Types"]');
        allTypesCheckbox.addEventListener('change', (e) => {
            entityTypeCheckboxes.forEach(checkbox => {
                if (checkbox.value !== 'All Types') {
                    checkbox.checked = false;
                    checkbox.disabled = e.target.checked;
                }
            });
        });

        // Add listeners for other checkboxes
        entityTypeCheckboxes.forEach(checkbox => {
            if (checkbox.value !== 'All Types') {
                checkbox.addEventListener('change', (e) => {
                    const allTypesCheckbox = document.querySelector('input[value="All Types"]');
                    if (e.target.checked) {
                        allTypesCheckbox.checked = false;
                    }
                });
            }
        });

        // Update the displayed value of the range input
        topEntitiesInput.addEventListener('input', () => {
            document.getElementById('topKValue').textContent = topEntitiesInput.value;
        });

        // Add submit button listener
        filterForm.addEventListener('submit', handleFilterSubmit);
    }
}

// Handle form submission
function handleFilterSubmit(event) {
    event.preventDefault();
    const submitButton = document.getElementById('filterSubmit');
    submitButton.disabled = true;
    submitButton.textContent = 'Updating...';

    handleFilterChange()
        .then(() => {
            submitButton.disabled = false;
            submitButton.textContent = 'Apply Filters';
        })
        .catch(error => {
            console.error('Error updating filters:', error);
            submitButton.disabled = false;
            submitButton.textContent = 'Apply Filters';
        });
}

// Handle filter change
async function handleFilterChange() {
    const entityTypeCheckboxes = document.querySelectorAll('input[name="entityType"]:checked');
    const selectedEntityTypes = Array.from(entityTypeCheckboxes).map(checkbox => checkbox.value);
    const topEntities = document.querySelector('input[data-filter="mentions"]').value;

    try {
        // Send a POST request to the server with the filter parameters
        const response = await fetch('/filter', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                entityType: selectedEntityTypes,
                topEntities: topEntities
            })
        });

        const data = await response.json();
        // Update the charts with the new data
        updateCharts(data);
    } catch (error) {
        console.error('Error fetching filtered data:', error);
        throw error;
    }
}

// Update charts with new data
function updateCharts(data) {
    const layoutDefaults = {
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: {
            family: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif'
        },
        margin: { t: 30, r: 20, b: 40, l: 100 },
        height: 400
    };

    // Update the bar chart
    if (data.bar_chart) {
        Plotly.newPlot('topEntities',
            JSON.parse(data.bar_chart),
            Object.assign({}, layoutDefaults, {
                xaxis: { gridcolor: '#eee' },
                yaxis: { gridcolor: '#eee' }
            })
        );
    }

    // Update the pie chart
    if (data.pie_chart) {
        Plotly.newPlot('entityDist',
            JSON.parse(data.pie_chart),
            Object.assign({}, layoutDefaults)
        );
    }
}