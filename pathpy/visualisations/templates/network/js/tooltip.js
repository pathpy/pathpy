define('tooltip',['d3'], function(d3){

  /*
   * Creates tooltip with provided id that
   * floats on top of visualization.
   * Most styling is expected to come from CSS
   * so check out bubble_chart.css for more details.
   */
  return function(tooltipId, width){

    // Local variable to hold tooltip div for
    // manipulation in other functions.
    var tt = d3.select('body')
        .append('div')
        .attr('class', 'tooltip')
        .attr('id', tooltipId)
        .style('pointer-events', 'none');

    // Set a width if it is provided.
    if (width) {
      tt.style('width', width);
    }

    // Initially it is hidden.
    hideTooltip();

    /*
     * Display tooltip with provided content.
     * content is expected to be HTML string.
     * event is d3.event for positioning.
     */
    function showTooltip(content, event) {
      tt.style('opacity', 1.0)
        .html(content);

      updatePosition(event);
    }

    /*
     * Hide the tooltip div.
     */
    function hideTooltip() {
      tt.style('opacity', 0.0);
    }

    /*
     * Figure out where to place the tooltip
     * based on d3 mouse event.
     */
    function updatePosition(event) {
      var xOffset = 20;
      var yOffset = 10;

      var ttw = tt.style('width');
      var tth = tt.style('height');

      var wscrY = window.scrollY;
      var wscrX = window.scrollX;

      var curX = (document.all) ? event.clientX + wscrX : event.pageX;
      var curY = (document.all) ? event.clientY + wscrY : event.pageY;
      var ttleft = ((curX - wscrX + xOffset * 2 + ttw) > window.innerWidth) ?
          curX - ttw - xOffset * 2 : curX + xOffset;

      if (ttleft < wscrX + xOffset) {
        ttleft = wscrX + xOffset;
      }

      var tttop = ((curY - wscrY + yOffset * 2 + tth) > window.innerHeight) ?
          curY - tth - yOffset * 2 : curY + yOffset;

      if (tttop < wscrY + yOffset) {
        tttop = curY + yOffset;
      }

      tt
        .style('top', tttop + 'px')
        .style('left', ttleft + 'px');
    }

    return {
      showTooltip: showTooltip,
      hideTooltip: hideTooltip,
      updatePosition: updatePosition
    };
  };
});
