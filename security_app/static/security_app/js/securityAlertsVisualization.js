// securityAlertsVisualization.js

// Function to create a bar chart for security alerts visualization
function createSecurityAlertsVisualization(containerId, securityAlerts) {
    // Select the container using D3
    var container = d3.select('#' + containerId);

    // Clear any existing content in the container
    container.html('');

    // Set up the data for the bar chart
    var data = securityAlerts.map(function(alert) {
        return { label: alert.type, value: alert.count };
    });

    // Set up the bar chart dimensions
    var chartWidth = 300;
    var chartHeight = 150;
    var margin = { top: 20, right: 30, bottom: 20, left: 30 };

    // Set up scales for the bar chart
    var xScale = d3.scaleBand().domain(data.map(d => d.label)).range([0, chartWidth]).padding(0.2);
    var yScale = d3.scaleLinear().domain([0, d3.max(data, d => d.value)]).range([chartHeight, 0]);

    // Create the SVG container
    var svg = container.append('svg').attr('width', chartWidth + margin.left + margin.right).attr('height', chartHeight + margin.top + margin.bottom);
    var chartGroup = svg.append('g').attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

    // Create bars in the chart
    chartGroup.selectAll('rect')
        .data(data)
        .enter()
        .append('rect')
        .attr('x', d => xScale(d.label))
        .attr('y', d => yScale(d.value))
        .attr('width', xScale.bandwidth())
        .attr('height', d => chartHeight - yScale(d.value))
        .attr('fill', '#2196F3');  // Blue color for demonstration

    // Add labels to the bars
    chartGroup.selectAll('text')
        .data(data)
        .enter()
        .append('text')
        .text(d => d.value)
        .attr('x', d => xScale(d.label) + xScale.bandwidth() / 2)
        .attr('y', d => yScale(d.value) - 5)
        .attr('text-anchor', 'middle')
        .attr('font-size', '12px');

    // Add axis labels
    chartGroup.append('g').attr('transform', 'translate(0,' + chartHeight + ')').call(d3.axisBottom(xScale));
    chartGroup.append('g').call(d3.axisLeft(yScale).ticks(5));

    // Add a title to the chart
    svg.append('text')
        .attr('x', chartWidth / 2 + margin.left)
        .attr('y', margin.top)
        .attr('text-anchor', 'middle')
        .attr('font-size', '16px')
        .text('Security Alerts');
}
