// passwordStrengthGauge.js


function _1(md){return(
  md`# passwordstrength`
  )}
  
function _data(){return(
  {"total": 100, "value": 20, "goal": 25}
  )}
function createPasswordStrengthGauge(containerId, passwordStrength) {
  // Define the color scale for different password strength levels
  const colorScale = d3.scaleLinear()
      .domain([0, 25, 50, 75, 100])
      .range(['#d9534f', '#f0ad4e', '#5bc0de', '#5cb85c', '#5cb85c']);

  // Set up the SVG container
  const width = 150;
  const height = 150;
  const svg = d3.select(`#${containerId}`)
      .append('svg')
      .attr('width', width)
      .attr('height', height);

  // Set up the meter properties
  const meterRadius = Math.min(width, height) / 2;
  const meterCenter = { x: width / 2, y: height / 2 };
  const meterStartAngle = -120;
  const meterEndAngle = 120;

  // Add the background arc for the meter
  svg.append('path')
      .attr('d', d3.arc()
          .innerRadius(meterRadius - 10)
          .outerRadius(meterRadius)
          .startAngle((meterStartAngle * Math.PI) / 180)
          .endAngle((meterEndAngle * Math.PI) / 180)
      )
      .attr('transform', `translate(${meterCenter.x}, ${meterCenter.y})`)
      .style('fill', '#eee');

  // Calculate the dynamic length of the pointer based on password strength
  const pointerLength = meterRadius - 10;
  const pointerWidth = 8;
  const pointerAngle = ((passwordStrength / 100) * (meterEndAngle - meterStartAngle) + meterStartAngle) * (Math.PI / 180);

  const pointerX = meterCenter.x + pointerLength * Math.cos(pointerAngle);
  const pointerY = meterCenter.y + pointerLength * Math.sin(pointerAngle);

  // Add the password strength arc
  const arc = d3.arc()
      .innerRadius(meterRadius - 10)
      .outerRadius(meterRadius)
      .startAngle((meterStartAngle * Math.PI) / 180)
      .endAngle(((passwordStrength / 100) * (meterEndAngle - meterStartAngle) + meterStartAngle) * (Math.PI / 180));

  svg.append('path')
      .datum({ endAngle: ((passwordStrength / 100) * (meterEndAngle - meterStartAngle) + meterStartAngle) * (Math.PI / 180) })
      .style('fill', colorScale(passwordStrength))
      .attr('d', arc)
      .attr('transform', `translate(${meterCenter.x}, ${meterCenter.y})`);

  // Add the pointer
  svg.append('line')
      .attr('x1', meterCenter.x)
      .attr('y1', meterCenter.y)
      .attr('x2', pointerX)
      .attr('y2', pointerY)
      .attr('stroke', '#333')
      .attr('stroke-width', pointerWidth);

  // Add text indicating password strength
  svg.append('text')
      .attr('x', meterCenter.x)
      .attr('y', meterCenter.y + meterRadius + 20)
      .attr('text-anchor', 'middle')
      .style('font-size', '16px')
      .style('fill', '#333')
      .text(`Strength: ${passwordStrength}%`);
}

// Example usage:
// createPasswordStrengthGauge('password-strength-container', 75);
