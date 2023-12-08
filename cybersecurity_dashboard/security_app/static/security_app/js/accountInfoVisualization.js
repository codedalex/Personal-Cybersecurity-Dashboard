// accountInfoVisualization.js

// Function to create an account information visualization
function createAccountInfoVisualization(containerId, accountCreatedTimestamp, accountUpdatedTimestamp) {
    // Select the container using D3
    var container = d3.select('#' + containerId);

    // Clear any existing content in the container
    container.html('');

    // Set up the data for the bar chart
    var data = [
        { label: 'Account Created', value: accountCreatedTimestamp },
        { label: 'Account Updated', value: accountUpdatedTimestamp },
    ];

    // Set up the SVG dimensions
    var svgWidth = 300;
    var svgHeight = 150;

    // Set up the scales for the bar chart
    var xScale = d3.scaleBand().domain(data.map(d => d.label)).range([0, svgWidth]).padding(0.2);
    var yScale = d3.scaleLinear().domain([0, d3.max(data, d => d.value)]).range([svgHeight, 0]);

    // Create the SVG container
    var svg = container.append('svg').attr('width', svgWidth).attr('height', svgHeight);

    // Create bars in the chart
    svg.selectAll('rect')
        .data(data)
        .enter()
        .append('rect')
        .attr('x', d => xScale(d.label))
        .attr('y', d => yScale(d.value))
        .attr('width', xScale.bandwidth())
        .attr('height', d => svgHeight - yScale(d.value))
        .attr('fill', '#2196F3');  // Blue color for demonstration

    // Add labels to the bars
    svg.selectAll('text')
        .data(data)
        .enter()
        .append('text')
        .text(d => d.value)
        .attr('x', d => xScale(d.label) + xScale.bandwidth() / 2)
        .attr('y', d => yScale(d.value) - 5)
        .attr('text-anchor', 'middle')
        .attr('font-size', '12px');

    // Add axis labels
    svg.append('g').attr('transform', 'translate(0,' + svgHeight + ')').call(d3.axisBottom(xScale));
    svg.append('g').call(d3.axisLeft(yScale).ticks(5));

    // Add a title to the chart
    svg.append('text')
        .attr('x', svgWidth / 2)
        .attr('y', 20)
        .attr('text-anchor', 'middle')
        .attr('font-size', '16px')
        .text('Account Information Visualization');
}
