define('network',['d3','tooltip'], function(d3,tooltip){

  /*
   * network
   */
  return function(config){

    // Constants for sizing
    var width = config.width || 400;
    var height = config.height || 400;
    var temporal = config.temporal || false;
    var tooltipSize = config.widgets.tooltip.size || '100px';

    var radiusMinSize = config.radiusMinSize || 4;
    var radiusMaxSize = config.radiusMaxSize || 16;
    // variables to refect the current settings
    // of the visualization
    var layout = config.layout || 'force';
    var filter = 'all';
    var time = {past:0,time:0,aggregated:0,future:0};

    // 'global' variables for the network
    // these will be populated in the setup
    // of the network
    var svg = null;
    var nodes = null;
    var edges = null;
    var allData = {};
    var linkedByIndex = {};
    var showEdges = true;
    var chargePower = 0.04;

    var countExtent = null;
    // colors for nodes
    // var colorScheme = d3.scaleOrdinal(d3.schemeCategory20);

    // tooltip for mouseover functionality
    // implemented in tooltip.js
    var myTooltip = tooltip('network-tooltip', tooltipSize);

    /*
3     * Charge function used to set the strength of
     * the many-body force.
     * Charge is negative because we want nodes to repel
     */
    function charge(d) {
      return -20;//-Math.pow(d.radius, 2.0) * chargePower;
    }

    /*
     * Callback executed after ever tick of the simulation
     */
    function ticked() {
      nodes
        .attr('cx', function (d) { return d.x; })
        .attr('cy', function (d) { return d.y; });

      if (showEdges) {
        edges
          .attr('x1', function (d) { return d.source.x; })
          .attr('y1', function (d) { return d.source.y; })
          .attr('x2', function (d) { return d.target.x; })
          .attr('y2', function (d) { return d.target.y; });
      } else {
        edges
          .attr('x1', 0)
          .attr('y1', 0)
          .attr('x2', 0)
          .attr('y2', 0);
      }
    }

    function ended() {
      showEdges = true;
      ticked();
    }

    // function transform(d) {
    //   return "translate(" + d.x + "," + d.y + ")";
    // }

    // Functions to enable draging of the nodes
    // see https://observablehq.com/@d3/force-directed-graph
    function dragstarted(d) {
      if (!d3.event.active) simulation.alphaTarget(0.2).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(d) {
      d.fx = d3.event.x;
      d.fy = d3.event.y;
    }

    function dragended(d) {
      if (!d3.event.active) simulation.alphaTarget(0.2);
      d.fx = null;
      d.fy = null;
    }

    var drag = d3.drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);


    //Zoom functions which transforms the element of the graph
    function zoomed(){
      svg.selectAll('g').attr("transform", d3.event.transform);
      // nodes.attr("transform", d3.event.transform)
      // edges.attr("transform", d3.event.transform)
    }

    //Zoom functions with key combination
    function zoomedWithKey(){
      // works only with pressed alt key
      if (d3.event.sourceEvent.shiftKey == false) return;
      svg.selectAll('g').attr("transform", d3.event.transform);
      // nodes.attr("transform", d3.event.transform)
      // edges.attr("transform", d3.event.transform)
    }

    // function to zoom in and out
    function transition(zoomLevel) {
      svg.transition()
        .delay(10)
        .duration(700)
        .call(zoom.scaleBy, zoomLevel);
    }

    // Zoom options
    var zoom = d3.zoom()
        .scaleExtent([1/2, 4])
        .extent([[0, 0], [width, height]])
        .on("zoom", zoomed);

    // Function which returns the object color if defined
    // otherwise a default value
    function getColor(d){
      if (typeof d.color === "undefined"){
        return "#99ccff";
      } 
      else return d.color;
      }
    }

    // Function which returns the object text if defined
    // otherwise a default value
    function getText(d){
      if (typeof d.text === "undefined"){
        return " "
      } else {
        return d.text
      }
    }

    // Function which returns the object weight if defined
    // otherwise a default value
    function getWeight(d){
      if (typeof d.weight === "undefined"){
        return 1
      } else {
        return d.weight
      }
    }

    // Function which returns the object weight if defined
    // otherwise a default value
    function getSize(d){
      if (typeof d.size === "undefined"){
        return 6
      } else {
        return d.size
      }
    }

    // Function which returns the object name if defined
    // otherwise a default value
    function getName(d){
      if (typeof d.label === "undefined"){
        return d.uid
      } else {
        return d.label
      }
    }

    // Here we create a force layout
    // It is just the 'simulation' and will have
    // forces added to it later
    var simulation = d3.forceSimulation()
        .velocityDecay(0.2)
        .alphaMin(0.1)
        .on('tick', ticked)
        .on('end', ended);


    // Simulation starts automatically,
    // We don't want it to start until it has
    // nodes so stop for now.
    simulation.stop();

    /*
     * Entry point to create network.
     * This function is returned by the
     * enclosing function and will be what is
     * executed when we have data to visualize.
     */
    var chart = function (selector, rawData) {
      allData = setupData(rawData);

      // create a SVG element inside the provided selector
      // with desired size.
      svg = d3.select(selector)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .call(d3.zoom()
              .scaleExtent([1/2, 4])
              .extent([[0, 0], [width, height]])
              .on("zoom", zoomedWithKey));

      // add some groups for edges and nodes
      svg.append('g')
        .attr('class', 'edges');

      svg.append('g')
        .attr('class', 'nodes');

      // render the network
      render();
    };

    /*
     * This function is executed any time the
     * network is modified. It filters the nodes
     * and edges based on the configuration of the
     * controls, sets up the force simulation, and
     * then restarts it to animate.
     */
    function render() {

      // filter data to show based on current filter settings.
      var filteredNodes = filterNodes(allData.nodes);
      var consideredNodes = filteredNodes;

      // if temporal network check if nodes change
      if (temporal === true){
      consideredNodes = updateTemporalNodes(
        filteredNodes,allData.changes);};

      // filter edges based on given nodes
      var filteredEdges = filterEdges(
        allData.links, consideredNodes);
      var considerdEdges = filteredEdges;

      // if temporal network check for the correct edges
      if (temporal === true){
        considerdEdges = filterTemporalEdges(filteredEdges);
      };

      // set the nodes of the simulation
      simulation.nodes(consideredNodes);

      // adjust the simulation based on
      // if the layout is force directed or euclidean
      if (layout === 'force') {
        // use a force directed layout
        setupNetworkLayout(considerdEdges);
      } else if(layout === 'euclidean'){
        // use an Euclidean layout
        setupEuclideanLayout();
      } else{
        // pre default use a force directed layout
        setupNetworkLayout(considerdEdges);
      }

      // render nodes and edges
      renderNodes(consideredNodes);
      renderEdges(considerdEdges);

      // render temporal edges if given
      if (temporal === true){
        renderTemporalEdges();
      };

      // Now we need to set the alpha
      // of the simulation when we restart.
      simulation.alpha(1).restart();
    }

    /*
     * Sets up simulation with forces needed
     * for regular force-directed layout.
     * Now we add separate forces to the simulation,
     * providing a name and a force function.
     * Reusing a force name will override any
     * existing force attached to it.
     */
    function setupNetworkLayout(edgesData) {
      // now edges and how they impact
      // the layout of the network is all
      // handled in a link force
      var linkForce = d3.forceLink()
          .distance(50)
          .strength(function(d){return getWeight(d);})
          .links(edgesData);

      // add the link force to the simulation
      simulation.force('links', linkForce);
      // setup a center force to keep nodes
      // in middle of the div
      simulation.force('center', d3.forceCenter(width / 2, height / 2));

      // setup many body force to have nodes repel one another
      // increasing the chargePower here to make nodes stand about
      chargePower = 1.0;
      simulation.force('charge', d3.forceManyBody().strength(charge));
      // kill x and y forces used in radial layout
      simulation.force('x', null);
      simulation.force('y', null);

      // setting taken from pathpy2
      // TODO fix theses setting

      // ingos setting
      // simulation.force("charge", d3.forceManyBody().strength(-20).distanceMax(400));
      // simulation.force("repelForce", d3.forceManyBody().strength(-200).distanceMax(100));
      // simulation.alphaTarget(0.0);

    }

    /*
     * Sets up simulation with forces needed
     * for euclidian layout.
     * Now we add separate forces to the simulation,
     * providing a name and a force function.
     * Reusing a force name will override any
     * existing force attached to it.
     */
    function setupEuclideanLayout() {
      // we don't want the center force
      // or links force affecting the network
      // in radial mode - so kill them.
      simulation.force('center', null);
      simulation.force('links', null);

      // use many-body force to reduce node overlap
      // in node clusters.
      chargePower = 1.00;
      simulation.force('charge', d3.forceManyBody().strength(charge));

      // generate a list for all x and y coordinates
      var xs = [];
      var ys = [];

      // get the coordinates of the nodes
      for (var key in allData.nodes) {
        var value = allData.nodes[key];
        xs.push(value.euclidean[0]);
        ys.push(value.euclidean[1]);
      }

      // find the min and the max coordinate
      var minX = d3.min(xs);
      var maxX = d3.max(xs);
      var minY = d3.min(ys);
      var maxY = d3.max(ys);

      // generate a scale function which allows to scale the node coordinate
      // to a coodinate at the html canvas, thereby 10px border are considerd
      var xScale = d3.scaleLinear()
          .domain([minX, maxX])
          .range([10,width-10]);

      var yScale = d3.scaleLinear()
          .domain([minY, maxY])
          .range([10,height-10]);

      // use the node coordinates to adjust x position of
      // nodes with an x force
      var xForce = d3.forceX()
          .strength(0.1)
          .x(function (d) { return xScale(d.euclidean[0]); });

      // use the node coordinates to adjust y position of
      // nodes with an y force
      var yForce = d3.forceY()
          .strength(0.1)
          .y(function (d) { return yScale(d.euclidean[1]); });


      // add these forces to the simulation
      simulation.force('x', xForce);
      simulation.force('y', yForce);
    }

    /*
     * Filter down nodes based on controls configuration
     */
    function filterNodes(nodesData) {
      var newNodesData = nodesData;

      // if other option than all is used filter groups accordingly
      if (filter !== 'all') {
        var groups = nodesData.map(function (d) { return d.group; });
        newNodesData = nodesData.filter(function (d) {
          if (filter === d.group){
            return d.group}
        });
      }

      return newNodesData;
    }

    /*
     * Filter down edges based on what nodes are
     * currently present in the network.
     */
    function filterEdges(edgesData, nodesData) {
      var nodesMap = d3.map(nodesData, function (d) { return d.uid; });

      var newEdgesData = edgesData.filter(function (d) {
        return nodesMap.get(d.source.uid) && nodesMap.get(d.target.uid);
      });

      return newEdgesData;
    }

    /*
     * Update attributes of the temporal Nodes
     */
    function updateTemporalNodes(nodesData,changesData) {

      // filter changes based on the current time step
      var newChanges = changesData.filter(function (d) {
        return (d.time === time.time);
      });

      var newUpdatedNodes = nodesData;

      // iterate through the changes
      newChanges.forEach(function (n){

        // find the index of the changed node
        var objIndex = newUpdatedNodes
            .findIndex((obj => obj.uid == n.uid));
        if (objIndex >= 0){
          // update node
          newUpdatedNodes[objIndex] = Object.assign(
            newUpdatedNodes[objIndex],n);};
       });

      // return the updated nodes
      return newUpdatedNodes;
    };

    /*
     * Filter down edges based on the time frame
     */
    function filterTemporalEdges(edgesData) {

      var newTemporalEdgesData = edgesData.filter(function (d) {
        return (d.time >= time.past && d.time <= time.future);
      });

      return newTemporalEdgesData;
    };

    /*
     * This performs the enter / exit / merge
     * d3 functionality for node data.
     */
    function renderNodes(nodesData) {
      nodes = svg.select('.nodes').selectAll('.node')
        .data(nodesData);

      var nodesE = nodes.enter().append('circle')
          .attr("r", 0)
          .classed('node', true)
          .classed('node_highlight',false)
          //.classed('node_search',false)
          .attr('cx', function (d) { return d.x; })
          .attr('cy', function (d) { return d.y; })
          .on('mouseover', highlightNode)
          .on('mouseout', unhighlightNode)
          .call(drag);

      nodes.exit()
        .transition() // transition to shrink node
        .attr("r", 0)
        .remove();

      nodes = nodes.merge(nodesE);
      nodes.transition() // transition to change size and color
        .attr('r', function (d) { return scaleRadius(d); })
        .style('fill', function (d) { return getColor(d); });
    }

    /*
     * This performs the enter / exit / merge
     * d3 functionality for edge data.
     */
    function renderEdges(edgesData) {
      edges = svg.select('.edges').selectAll('.edge')
        .data(edgesData, function (d) { return d.uid; });

      var edgesE = edges.enter().append('line')
          .classed('edge', true)
          .classed('edge_active', true)
          .classed('edge_highlight', false);

      edges.exit().remove();

      edges = edges.merge(edgesE);
    }

    /*
     * Disable observed but not active edges
     */
    function renderTemporalEdges() {
      edges.classed('edge_active',function(d){
        if ((d.time >= time.past && d.time < time.time)||
            (d.time > time.aggregated && d.time <= time.future)){
          return false;
        }else{
          return true;
        }
      });
    };

    function scaleRadius(n){
      var radiusScale = d3.scaleLinear()
          .range([radiusMinSize, radiusMaxSize])
          .domain(countExtent);
      return radiusScale(getSize(n));
    };

    /*
     * Called when data is updated,
     * sets up scales to be appropriate for the
     * currently selected data.
     * Transforms node Id's to node objects for
     * edge data.
     */
    function setupData(data) {

      // get config values
      // width = data.config.width
      // height = data.config.height

      // initialize circle radius scale
      countExtent = d3.extent(data.nodes, function (d) { return getSize(d); });
      // var radiusScale = d3.scalePow()
      //     .exponent(0.5)
      //     .range([3, 12])
      //     .domain(countExtent);


      data.nodes.forEach(function (n) {
        // add radius to the node so we can use it later
        n.radius = scaleRadius(n);
      });

      var nodesMap = d3.map(data.nodes, function (d) { return d.uid; });

      // switch links to point to node objects instead of id's
      data.links.forEach(function (l) {
        l.source = nodesMap.get(l.source);
        l.target = nodesMap.get(l.target);
        l.uid = l.source.uid + '_' + l.target.uid;

        // linkedByIndex is used for link sorting
        linkedByIndex[l.uid] = 1;
      });

      return data;
    }

    /*
     * Public function to reset the zoom.
     * Most of the work happens in render()
     */
    chart.updateZoom = function (newZoom){
      if (newZoom === 'zoom_in'){
        transition(1.2); // increase on 0.2 each time
      }
      if (newZoom === 'zoom_out'){
        transition(0.8); // deacrease on 0.2 each time
      }
      if (newZoom === 'zoom_init'){
        svg.transition()
          .delay(100)
          .duration(700)
          .call(zoom.transform, d3.zoomIdentity); // return to initial state
      }
      render();
    }

    /*
     * Public function to update the layout.
     * Most of the work happens in render()
     */
    chart.updateLayout = function (newLayout) {
      layout = newLayout;
      showEdges = true;//layout === 'force';
      render();
      return this;
    };


    /*
     * Public function to update node filters.
     * Most of the work happens in render()
     */
    chart.updateFilter = function (newFilter) {
      filter = newFilter;
      render();
      return this;
    };

    /*
     * Public function to update the temporal network.
     * Most of the work happens in render()
     */
    chart.updateTime = function (newTime) {
      //console.log('new time',newTime);
      time = newTime;
      render();
      return this;
    };


    /*
     * Public function to update input data
     * Most of the work happens in render()
     */
    chart.updateData = function (newData) {
      allData = setupData(newData);
      render();
    };


    /*
     * Public function to handle search.
     * Updates nodes if a match is found.
     */
    chart.updateSearch = function (searchTerm) {
      var searchRegEx = new RegExp(searchTerm.toLowerCase());
      nodes.each(function (d) {
        var element = d3.select(this)
            .classed('node_search',false);
        var match = getName(d).toLowerCase().search(searchRegEx);
        if (searchTerm.length > 0 && match >= 0) {
          element.classed('node_search',true)
            .style('fill', '#F38630');
          d.searched = true;
        } else {
          d.searched = false;
          element.classed('node_search',false);
          element.style('fill', function (e) { return getColor(e); });
        }
      });
    };

    /*
     * Public function to return the svg canvas
     */
    chart.getSVG = function () {
      return svg;
    };

    /*
     * Callback for mouseover event.
     * Highlights a node and connected edges.
     */
    function highlightNode(d) {
      var content = '<p class="main">' + getName(d) + '</span></p>';
      content += '<hr class="tooltip-hr">';
      content += '<p class="main">' + getText(d) + '</span></p>';
      myTooltip.showTooltip(content, d3.event);

      if (showEdges) {
        edges
          .classed('edge_highlight', function (l) {
            if (l.source.uid === d.uid || l.target.uid === d.uid) {
              return true;
            }
            return false;
          });

        // higlight connected nodes
        nodes
          .classed('node_highlight', function (n) {
            if (d.uid === n.uid || n.searched || neighboring(d, n)) {
              return true;
            }
            return false;
          });
      }
    }

    /*
     * Helper function returns not-false
     * if a and b are connected by an edge.
     * Uses linkedByIndex object.
     */
    function neighboring(a, b) {
      return linkedByIndex[a.uid + '_' + b.uid] ||
        linkedByIndex[b.uid + '_' + a.uid];
    }

    /*
     * Callback for mouseout event.
     * Unhighlights node.
     */
    function unhighlightNode() {
      myTooltip.hideTooltip();

      // reset edges
      edges
        .classed('edge_highlight',false);

      // reset nodes
      nodes
        .classed('node_highlight',false);
    }

    return chart;
  };
}); // End of define
