// loginInfoVisualization.js

// Function to create a login information visualization
function createLoginInfoVisualization(containerId, loginAttempts, successfulLogins, failedLoginTimestamp) {
  // Select the container using D3
  const container = d3.select(`#${containerId}`);

  // Clear any existing content in the container
  container.html('');

  // Set up the data for the bar chart
  const data = [
    { label: 'Login Attempts', value: loginAttempts || 0 },
    { label: 'Successful Logins', value: successfulLogins || 0 },
    { label: 'Failed Login Timestamp', value: failedLoginTimestamp ? 1 : 0 },
  ];

  // Set up the SVG dimensions
  const svgWidth = 300;
  const svgHeight = 150;

  // Set up the scales for the bar chart
  const xScale = d3.scaleBand().domain(data.map(d => d.label)).range([0, svgWidth]).padding(0.2);
  const yScale = d3.scaleLinear().domain([0, d3.max(data, d => d.value)]).range([svgHeight, 0]);

  // Create the SVG container
  const svg = container.append('svg').attr('width', svgWidth).attr('height', svgHeight);

  // Create bars in the chart
  svg.selectAll('rect')
    .data(data)
    .enter()
    .append('rect')
    .attr('x', d => xScale(d.label) || 0)
    .attr('y', d => yScale(d.value))
    .attr('width', xScale.bandwidth() || 0)
    .attr('height', d => svgHeight - yScale(d.value))
    .attr('fill', '#4CAF50');  // Green color for demonstration

  // Add labels to the bars
  svg.selectAll('text')
    .data(data)
    .enter()
    .append('text')
    .text(d => d.value)
    .attr('x', d => (xScale(d.label) || 0) + xScale.bandwidth() / 2)
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
    .text('Login Information Visualization');
}

// Call the function with the provided data
createLoginInfoVisualization('login-info-container', 0, 0, '');


