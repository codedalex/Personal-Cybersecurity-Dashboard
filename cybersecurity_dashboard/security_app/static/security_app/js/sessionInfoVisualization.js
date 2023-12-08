// sessionInfoVisualization.js

// Function to create a line chart for session information visualization
function createSessionInfoVisualization(containerId, activeSessions) {
    // Select the container using D3
    var container = d3.select('#' + containerId);

    // Clear any existing content in the container
    container.html('');

    // Parse timestamps and format data for the line chart
    var parseTime = d3.timeParse('%Y-%m-%dT%H:%M:%S.%LZ');
    var data = activeSessions.map(function (d) {
        return { timestamp: parseTime(d.timestamp), session: d.session };
    });

    // Set up the line chart dimensions
    var margin = { top: 20, right: 30, bottom: 30, left: 50 },
        width = 600 - margin.left - margin.right,
        height = 300 - margin.top - margin.bottom;

    // Set up the scales for the line chart
    var x = d3.scaleTime().range([0, width]);
    var y = d3.scaleLinear().range([height, 0]);

    // Create the line function
    var line = d3.line()
        .x(function (d) { return x(d.timestamp); })
        .y(function (d) { return y(d.session); });

    // Create the SVG container
    var svg = container.append('svg')
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

    // Set the domains of the scales
    x.domain(d3.extent(data, function (d) { return d.timestamp; }));
    y.domain([0, d3.max(data, function (d) { return d.session; })]);

    // Add the line to the chart
    svg.append('path')
        .data([data])
        .attr('class', 'line')
        .attr('d', line);

    // Add the X Axis
    svg.append('g')
        .attr('transform', 'translate(0,' + height + ')')
        .call(d3.axisBottom(x));

    // Add the Y Axis
    svg.append('g')
        .call(d3.axisLeft(y));

    // Add a title to the chart
    svg.append('text')
        .attr('x', width / 2)
        .attr('y', 0 - margin.top / 2)
        .attr('text-anchor', 'middle')
        .attr('font-size', '16px')
        .text('Active Sessions Over Time');
}

// Call the function to create the session information visualization
// Adjust the parameters based on your actual data structure
createSessionInfoVisualization('session-info-container', {{ active_sessions|safe }});
