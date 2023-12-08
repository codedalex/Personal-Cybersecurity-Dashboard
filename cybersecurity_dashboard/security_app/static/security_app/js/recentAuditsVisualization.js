// recentAuditsVisualization.js

// Function to create a bar chart for recent audits visualization
function createRecentAuditsVisualization(containerId, recentAudits) {
    // Select the container using D3
    var container = d3.select('#' + containerId);

    // Clear any existing content in the container
    container.html('');

    // Extract action frequencies from recent audits
    var actionFrequencies = {};
    recentAudits.forEach(function (audit) {
        var action = audit.action;
        actionFrequencies[action] = (actionFrequencies[action] || 0) + 1;
    });

    // Convert action frequencies to an array
    var data = Object.keys(actionFrequencies).map(function (action) {
        return { action: action, frequency: actionFrequencies[action] };
    });

    // Set up the bar chart dimensions
    var barChartOptions = {
        width: 300,
        height: 200,
        margin: { top: 20, right: 20, bottom: 30, left: 40 },
        color: d3.scaleOrdinal().range(['#2196F3']), // Blue color for demonstration
    };

    // Set up the scales for the bar chart
    var xScale = d3.scaleBand().domain(data.map(d => d.action)).range([0, barChartOptions.width]).padding(0.1);
    var yScale = d3.scaleLinear().domain([0, d3.max(data, d => d.frequency)]).range([barChartOptions.height, 0]);

    // Create the SVG container
    var svg = container.append('svg').attr('width', barChartOptions.width + barChartOptions.margin.left + barChartOptions.margin.right)
        .attr('height', barChartOptions.height + barChartOptions.margin.top + barChartOptions.margin.bottom)
        .append('g').attr('transform', 'translate(' + barChartOptions.margin.left + ',' + barChartOptions.margin.top + ')');

    // Create bars in the chart
    svg.selectAll('rect')
        .data(data)
        .enter()
        .append('rect')
        .attr('x', d => xScale(d.action))
        .attr('y', d => yScale(d.frequency))
        .attr('width', xScale.bandwidth())
        .attr('height', d => barChartOptions.height - yScale(d.frequency))
        .attr('fill', d => barChartOptions.color(d.action));

    // Add labels to the bars
    svg.selectAll('text')
        .data(data)
        .enter()
        .append('text')
        .text(d => d.frequency)
        .attr('x', d => xScale(d.action) + xScale.bandwidth() / 2)
        .attr('y', d => yScale(d.frequency) - 5)
        .attr('text-anchor', 'middle')
        .attr('font-size', '12px');

    // Add axis labels
    svg.append('g').attr('transform', 'translate(0,' + barChartOptions.height + ')').call(d3.axisBottom(xScale));
    svg.append('g').call(d3.axisLeft(yScale).ticks(5));

    // Add a title to the chart
    svg.append('text')
        .attr('x', barChartOptions.width / 2)
        .attr('y', 0 - (barChartOptions.margin.top / 2))
        .attr('text-anchor', 'middle')
        .attr('font-size', '16px')
        .text('Recent Audits Visualization');
}

// Call the function with the provided data
createRecentAuditsVisualization('recent-audits-container', {{ recent_audits|safe }});
