// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
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
        const chartData = JSON.parse(chartsContainer.getAttribute('data-charts'));
        
        // Create all charts
        createCharts(chartData);
        
    } catch (error) {
        console.error('Error initializing dashboard:', error);
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
        margin: { t: 30, r: 20, b: 40, l: 100 }
    };

    // Create Top Entities chart
    Plotly.newPlot('topEntities', 
        JSON.parse(chartData.top_entities),
        Object.assign({}, layoutDefaults, {
            height: 400,
            xaxis: { gridcolor: '#eee' },
            yaxis: { gridcolor: '#eee' }
        })
    );

    // Create Mentions Over Time chart
    Plotly.newPlot('mentionsTime', 
        JSON.parse(chartData.mentions_time),
        Object.assign({}, layoutDefaults, {
            height: 400,
            xaxis: { gridcolor: '#eee' },
            yaxis: { gridcolor: '#eee' }
        })
    );

    // Create Entity Distribution chart
    Plotly.newPlot('entityDist', 
        JSON.parse(chartData.entity_dist),
        Object.assign({}, layoutDefaults, {
            height: 400
        })
    );
}

// Setup filter event listeners
function setupFilterListeners() {
    // Entity Type filter
    const entityTypeInput = document.querySelector('[data-filter="entityType"]');
    if (entityTypeInput) {
        entityTypeInput.addEventListener('change', handleFilterChange);
    }

    // Date Range filter
    const dateRangeInput = document.querySelector('[data-filter="dateRange"]');
    if (dateRangeInput) {
        dateRangeInput.addEventListener('change', handleFilterChange);
    }

    // Minimum Mentions filter
    const mentionsInput = document.querySelector('[data-filter="mentions"]');
    if (mentionsInput) {
        mentionsInput.addEventListener('input', handleFilterChange);
    }

    // Location filter
    const locationInput = document.querySelector('[data-filter="location"]');
    if (locationInput) {
        locationInput.addEventListener('change', handleFilterChange);
    }
}

// Handle filter changes
function handleFilterChange(event) {
    const filterValue = event.target.value;
    const filterType = event.target.getAttribute('data-filter');
    
    console.log(`Filter changed: ${filterType} = ${filterValue}`);
    // Here you would typically make an AJAX call to your backend to get filtered data
    // Then update the charts with the new data
}

// Pagination handlers
function handlePagination(page) {
    console.log(`Navigating to page: ${page}`);
    // Implement pagination logic here
}

// Window resize handler for responsive charts
window.addEventListener('resize', function() {
    const charts = document.querySelectorAll('.chart');
    charts.forEach(chart => {
        Plotly.Plots.resize(chart);
    });
});

