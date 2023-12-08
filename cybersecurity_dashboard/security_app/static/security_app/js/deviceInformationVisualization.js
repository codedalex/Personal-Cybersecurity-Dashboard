// deviceInformationVisualization.js

// Function to create a line chart for device usage over time
function createDeviceUsageLineChart(containerId, deviceHistory) {
    // Parse timestamp strings to Date objects
    deviceHistory.forEach(entry => {
        entry.timestamp = new Date(entry.timestamp);
    });

    // Set up the dimensions and margins of the graph
    var margin = { top: 20, right: 30, bottom: 30, left: 60 },
        width = 600 - margin.left - margin.right,
        height = 400 - margin.top - margin.bottom;

    // Append the SVG object to the specified container
    var svg = d3
        .select(`#${containerId}`)
        .append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', `translate(${margin.left},${margin.top})`);

    // X and Y scales
    var x = d3
        .scaleTime()
        .domain(d3.extent(deviceHistory, d => d.timestamp))
        .range([0, width]);

    var y = d3
        .scaleLinear()
        .domain([0, d3.max(deviceHistory, d => d.devices)])
        .range([height, 0]);

    // Line function
    var line = d3
        .line()
        .x(d => x(d.timestamp))
        .y(d => y(d.devices));

    // Add the line
    svg.append('path')
        .datum(deviceHistory)
        .attr('fill', 'none')
        .attr('stroke', 'steelblue')
        .attr('stroke-width', 1.5)
        .attr('d', line);

    // Add X and Y axis
    svg.append('g')
        .attr('transform', `translate(0,${height})`)
        .call(d3.axisBottom(x));

    svg.append('g').call(d3.axisLeft(y));

    // Add labels
    svg.append('text')
        .attr('transform', `translate(${width / 2},${height + margin.top + 20})`)
        .style('text-anchor', 'middle')
        .text('Time');

    svg.append('text')
        .attr('transform', 'rotate(-90)')
        .attr('y', 0 - margin.left)
        .attr('x', 0 - height / 2)
        .attr('dy', '1em')
        .style('text-anchor', 'middle')
        .text('Number of Devices');
}

// Function to create a pie chart for device type distribution
function createDeviceTypeDistributionChart(containerId, deviceHistory) {
    // Implement the pie chart using D3.js
    // This example assumes deviceHistory is an array of objects with a 'type' property

    // Calculate device type distribution
    var deviceTypes = d3
        .nest()
        .key(d => d.type)
        .entries(deviceHistory);

    // Set up dimensions and margins
    var width = 400,
        height = 400,
        radius = Math.min(width, height) / 2;

    // Set up color scale
    var color = d3.scaleOrdinal(d3.schemeCategory10);

    // Create SVG container
    var svg = d3
        .select(`#${containerId}`)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .append('g')
        .attr('transform', `translate(${width / 2},${height / 2})`);

    // Generate pie chart data
    var pie = d3.pie().value(d => d.values.length);
    var data_ready = pie(deviceTypes);

    // Build arcs and bind data
    svg.selectAll('slices')
        .data(data_ready)
        .enter()
        .append('path')
        .attr('d', d3.arc().innerRadius(0).outerRadius(radius))
        .attr('fill', d => color(d.data.key))
        .attr('stroke', 'black')
        .style('stroke-width', '2px')
        .style('opacity', 0.7);

    // Add a legend
    var legend = svg
        .selectAll('.legend')
        .data(data_ready)
        .enter()
        .append('g')
        .attr('class', 'legend')
        .attr('transform', (d, i) => `translate(0,${i * 20})`);

    legend
        .append('rect')
        .attr('x', 30)
        .attr('width', 18)
        .attr('height', 18)
        .style('fill', d => color(d.data.key));

    legend
        .append('text')
        .attr('x', 60)
        .attr('y', 9)
        .attr('dy', '.35em')
        .style('text-anchor', 'start')
        .text(d => d.data.key);
}

// Function to create a timeline chart for device history
function createDeviceHistoryTimeline(containerId, deviceHistory) {
    // Implement the timeline chart using a library like vis.js
    // This example assumes deviceHistory is an array of objects with timestamp and device information

    // Create a DataSet with the data
    var timelineData = new vis.DataSet(
        deviceHistory.map(entry => ({
            id: entry.timestamp,
            content: entry.device,
            start: entry.timestamp,
        }))
    );

    // Set up the timeline options
    var options = {
        height: '300px',
        showCurrentTime: false,
        zoomMax: 31536000000, // 1 year
        format: {
            minorLabels: {
                minute: 'h:mma',
                hour: 'ha',
            },
        },
    };

    // Create the timeline
    var timeline = new vis.Timeline(document.getElementById(containerId), timelineData, options);
}

// Function to create a network graph for device interaction
function createDeviceInteractionGraph(containerId, deviceHistory) {
    // Implement the network graph using a library like vis.js
    // This example assumes deviceHistory is an array of objects with device interactions

    // Create nodes and edges from device interactions
    var nodes = [];
    var edges = [];

    deviceHistory.forEach((entry, index) => {
        // Add nodes
        nodes.push({ id: index, label: entry.device });

        // Add edges
        if (index > 0) {
            edges.push({ from: index - 1, to: index });
        }
    });

    // Set up data
    var graphData = {
        nodes: new vis.DataSet(nodes),
        edges: new vis.DataSet(edges),
    };

    // Set up options
    var options = {
        interaction: { hover: true },
        physics: { enabled: true },
    };

    // Create the network graph
    var network = new vis.Network(document.getElementById(containerId), graphData, options);
}

// Function to create a geospatial map for device location
function createDeviceLocationMap(containerId, locationHistory) {
    // Implement the geospatial map using a library like Leaflet
    // This example assumes locationHistory is an array of objects with latitude, longitude, and device information

    // Initialize the map
    var map = L.map(containerId).setView([0, 0], 2);

    // Add the base map layer
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
    }).addTo(map);

    // Add markers for each device location
    locationHistory.forEach(entry => {
        L.marker([entry.latitude, entry.longitude])
            .addTo(map)
            .bindPopup(entry.device);
    });
}

// Function to create a dashboard with gauges or indicators for device health
function createDeviceHealthDashboard(containerId, deviceHistory) {
    // Implement the dashboard using a library like JustGage
    // This example assumes deviceHistory is an array of objects with health-related information

    // Extract health data
    var healthData = deviceHistory.map(entry => entry.health);

    // Calculate average health
    var averageHealth = healthData.reduce((sum, value) => sum + value, 0) / healthData.length;

    // Set up JustGage options
    var options = {
        id: containerId,
        value: averageHealth,
        min: 0,
        max: 100,
        title: 'Device Health',
        label: 'Average Health',
        levelColors: ['#FF0000', '#FFD700', '#00FF00'], // Red, Yellow, Green
    };

    // Create the gauge
    var gauge = new JustGage(options);
}
// Function to create a dashboard with gauges or indicators for device health
createDeviceUsageLineChart('device-usage-line-chart', "{{ device_history|safe }}");
createDeviceTypeDistributionChart('device-type-distribution-chart', "{{ device_history|safe }}");
createDeviceHistoryTimeline('device-history-timeline', "{{ device_history|safe }}");
createDeviceInteractionGraph('device-interaction-graph', "{{ device_history|safe }}");
createDeviceLocationMap('device-location-map', "{{ location_history|safe }}");
createDeviceHealthDashboard('device-health-dashboard', "{{ device_history|safe }}");

