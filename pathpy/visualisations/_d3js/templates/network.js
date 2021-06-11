require(['d3'], function(d3){ //START
  console.log("Network Template Loaded");
  /* Resources

    https://bl.ocks.org/mapio/53fed7d84cd1812d6a6639ed7aa83868
    https://codepen.io/smlo/pen/JdMOej
  */

  // variables from the config file
  const selector = config.selector;
  const width = config.width || 400;
  const height = config.height || 400;

  /* Create a svg element to display the network */
  var svg = d3.select(selector)
      .append('svg')
      .attr('width', width)
      .attr('height', height)

  // add container to store the elements
  var container = svg.append("g");

  /*Add zoom function to the container */
  svg.call(
    d3.zoom()
      .scaleExtent([.1, 4])
      .on("zoom", function() { container.attr("transform", d3.event.transform); })
  );

  /*Load nodes and links from the data */
  var nodes = data.nodes
  var links = data.edges

  /*Link creation template */
  var link = container.append("g").attr("class", "links")
      .selectAll(".link")
      .data(links)
      .enter()
      .append("line")
      .attr("class", "link")
      .style("stroke", function(d) { return d.color; })
      .style("stroke-opacity", function(d) { return d.opacity; })
      .style("stroke-width", function(d){  return d.size });

  /*Node creation template */
  var node = container.append("g").attr("class", "nodes")
      .selectAll("circle.node")
      .data(nodes)
      .enter().append("circle")
      .attr("class", "node")
      .attr("x", function(d) { return d.x; })
      .attr("y", function(d) { return d.y; })
      .style("fill", function(d) { return d.color; })
      .style("opacity", function(d) { return d.opacity; })
      .style("r", function(d){  return d.size });

  /*Simulation of the forces*/
  var simulation = d3.forceSimulation(nodes)
      .force("charge", d3.forceManyBody().strength(-3000))
      .force("center", d3.forceCenter(width / 2, height / 2))
      .force("x", d3.forceX(width / 2).strength(1))
      .force("y", d3.forceY(height / 2).strength(1))
      .force("links", d3.forceLink(links)
             .id(function(d) {return d.uid; })
             .distance(50).strength(1))
      .on("tick", ticked);

  /*Update of the node and edge objects*/
  function ticked() {
    node.call(updateNode);
    link.call(updateLink);
  };

  /*Update link positions */
  function updateLink(link) {
    link
      .attr("x1", function(d) { return d.source.x; })
      .attr("y1", function(d) { return d.source.y; })
      .attr("x2", function(d) { return d.target.x; })
      .attr("y2", function(d) { return d.target.y; });
  };

  /*Update node positions */
  function updateNode(node) {
    node.attr("transform", function(d) {
      return "translate(" + d.x + "," + d.y + ")";
    });
  };

  /*Add drag functionality to the node objects*/
  node.call(
    d3.drag()
      .on("start", dragstarted)
      .on("drag", dragged)
      .on("end", dragended)
  );

  function dragstarted(d) {
    d3.event.sourceEvent.stopPropagation();
    if (!d3.event.active) simulation.alphaTarget(0.3).restart();
    d.fx = d.x;
    d.fy = d.y;
  };

  function dragged(d) {
    d.fx = d3.event.x;
    d.fy = d3.event.y;
  };

  function dragended(d) {
    if (!d3.event.active) simulation.alphaTarget(0);
    d.fx = null;
    d.fy = null;
  };

}); //END
