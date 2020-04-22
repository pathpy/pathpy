define('widgets',['d3','tooltip'], function(d3,tooltip){

  // Activate selector button
  function activate(group, link) {
    d3.selectAll('#' + group + ' button')
      .classed('active', false);
    d3.select('#' + group + ' #' + link)
      .classed('active', true);
  }

  function getTooltip(config,control){
    var title = config.widgets[control].title;
    var text = config.widgets[control].tooltip;
    var content = '<p class="main">' + title + '</span></p>';
    content += '<hr class="tooltip-hr">';
    content += '<p class="main">' + text + '</span></p>';
    return content
  };

  function setupMenu(container,config,network){

    // tooltip for mouseover functionality
    // implemented in tooltip.js
    var myTooltip = tooltip('menu-tooltip');

    // create menu bar which contains the control widgets
    var menuBar = d3.select(container)
        .append('div')
        .attr('class','pp_container')
        .attr('id','#pp_container');
      //.text("Second paragraph.");

    // container for the buttons
    var controlBar = menuBar
        .append('div')
        .attr('class','controls')
        .attr('id','#controls');

    // container of the save buttons
    var saveControl = d3.create('div')
        .attr('class','control')
        .attr('id','save')
        .on('mouseover', function () {
          myTooltip.showTooltip(getTooltip(config,'save'), d3.event);})
        .on("mouseout",function () {
          myTooltip.hideTooltip();});

    // save svg button
    var svgBtn = d3.create('button')
        .text('svg')
        .on('click', function () {

          // get the network svg
          var SVGElem = network.getSVG().node();
          var oDOM = SVGElem.cloneNode(true)
          // convert svg in order to include css styles
          convertSVG(oDOM, SVGElem)
          // serialize our SVG XML to a string.
          var data = new XMLSerializer().serializeToString(oDOM);
          // create a blob object
          var svg = new Blob([data], { type: "image/svg+xml;charset=utf-8" });
          // create data url
          var url = URL.createObjectURL(svg);

          // construct the 'a' element
          var link = window.document.createElement('a');
          link.download = 'network.svg'
          // construct the URI
          link.href = url;
          document.body.appendChild(link);
          link.click();
          // clean-up the DOM
          document.body.removeChild(link);
        });



    // save png button
    var pngBtn = d3.create('button')
        .text('png')
        .on('click', function () {

          // get the network svg
          var SVGElem = network.getSVG().node();
          var oDOM = SVGElem.cloneNode(true)
          // convert svg in order to include css styles
          convertSVG(oDOM, SVGElem)
          // serialize our SVG XML to a string.
          var data = new XMLSerializer().serializeToString(oDOM);
          // create a blob object
          var svg = new Blob([data], { type: "image/svg+xml;charset=utf-8" });
          // create data url
          var url = URL.createObjectURL(svg);

          // create image
          var img = d3.select('body')
              .append('img')
              .classed('exportImg', true).node();
          img.onload = function () {
            var canvas = document.createElement('canvas'),
                ctx = canvas.getContext('2d');
            canvas.width = config.width || 400;
            canvas.height = config.height || 400;
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            ctx.drawImage(img, 0, 0, canvas.width, canvas.height);
            d3.select('img.exportImg').remove();

            // construct the 'a' element
            var link = window.document.createElement('a');
            link.download = 'network.png'
            // construct the URI
            link.href = canvas.toDataURL();
            document.body.appendChild(link);
            link.click();
            // clean-up the DOM
            document.body.removeChild(link);

          };
          img.src = url;

          console.log('Save png')
          //network.getCanvas();
        });

    // assign button to the save
    saveControl.append(function(){ return svgBtn.node(); });
    saveControl.append(function(){ return pngBtn.node(); });


    // container of the zoom buttons
    var zoomControl = d3.create('div')
        .attr('class','control pp_vl')
        .attr('id','zoom')
        .on('mouseover', function () {
          myTooltip.showTooltip(getTooltip(config,'zoom'), d3.event);})
        .on("mouseout",function () {
          myTooltip.hideTooltip();});


    // zoom out button
    var zoomOutBtn = d3.create('button')
        .text('-')
        .on('click', function () {
          network.updateZoom('zoom_out');
        });

    // zoom reset button
    var zoomInitBtn = d3.create('button')
        .text('Reset')
        .on('click', function () {
          network.updateZoom('zoom_init');
        });

    // zoom in button
    var zoomInBtn = d3.create('button')
        .text('+')
        .on('click', function () {
          network.updateZoom('zoom_in');
        });

    // assign button to the zoom
    zoomControl.append(function(){ return zoomOutBtn.node(); });
    zoomControl.append(function(){ return zoomInitBtn.node(); });
    zoomControl.append(function(){ return zoomInBtn.node(); });

    // container of the layout buttons
    var layoutControl = d3.create('div')
        .attr('class','control pp_vl')
        .attr('id','layout')
        .on('mouseover', function () {
          myTooltip.showTooltip(getTooltip(config,'layout'), d3.event);})
        .on("mouseout",function () {
          myTooltip.hideTooltip();});

    // force directed layout button
    var forceBtn = d3.create('button')
        .attr('class','active')
        .attr('id','force')
        .text('Force')
        .on('click', function () {
          activate('layout', 'force');
          network.updateLayout('force');
        });

    // euclidean layout button
    var euclideanBtn = d3.create('button')
        .attr('id','euclidean')
        .text('Euclidean')
        .on('click', function () {
          activate('layout', 'euclidean');
          network.updateLayout('euclidean');
        });

    // assign button to the layout
    layoutControl.append(function(){ return forceBtn.node(); });
    if (config.euclidean === true){
      layoutControl.append(function(){ return euclideanBtn.node(); });};


    // container of the group drop down menu
    var filterControle = d3.create('div')
        .attr('class','control pp_vl')
        .attr('id','filter')
        .on('mouseover', function () {
          myTooltip.showTooltip(getTooltip(config,'filter'), d3.event);})
        .on("mouseout",function () {
          myTooltip.hideTooltip();});


    // initialize the drop down menu
    var groupDropDown = filterControle
        .append('select');

    // Create data = list of groups
    var allGroups = config.widgets.filter.groups

    // add the options to the button
    groupDropDown // Add a button
      .selectAll('myOptions') // Next 4 lines add 6 options = 6 colors
      .data(allGroups)
      .enter()
      .append('option')
      .text(function (d) { return d; }) // text showed in the menu
      .attr("value", function (d) { return d; }); // corresponding value returned by the button

    // add function by change
    groupDropDown
      .on('change', function () {
        var newFilter = d3.select(this).property('value');
        network.updateFilter(newFilter);
      });

    // container of the search buttons
    var searchControl = d3.create('div')
        .attr('class','control pp_vl')
        .attr('id','pp_search')
        .on('mouseover', function () {
          myTooltip.showTooltip(getTooltip(config,'search'), d3.event);})
        .on("mouseout",function () {
          myTooltip.hideTooltip();});


    searchControl
      .append('from')
      .attr('id','pp_search_from')
      .attr('action','')
      .attr('method','post')
    searchControl
      .append('input')
      .attr('type','text')
      .attr('class','text-input')
      .attr('id','search')
      .attr('value','')
      .attr('placeholder','Search ...')
      .on('keyup', function () {
        var searchTerm = d3.select(this).property('value');
        network.updateSearch(searchTerm);
      });


    // assign controls to widget if enabled
    if (config.widgets.save.enabled === true){
      controlBar.append(function(){ return saveControl.node(); });};
    if (config.widgets.zoom.enabled === true){
      controlBar.append(function(){ return zoomControl.node(); });};
    if (config.widgets.layout.enabled === true){
      controlBar.append(function(){ return layoutControl.node(); });};
    if (config.widgets.filter.enabled === true){
      controlBar.append(function(){ return filterControle.node(); });};
    if (config.widgets.search.enabled === true){
      controlBar.append(function(){ return searchControl.node(); });};

    function convertSVG(ParentNode, OrigData){
      var ContainerElements = ["svg","g"];
      var RelevantStyles = {"rect":["fill","stroke","stroke-width"],"path":["fill","stroke","stroke-width"],"circle":["fill","stroke","stroke-width"],"line":["stroke","stroke-width"],"text":["fill","font-size","text-anchor"],"polygon":["stroke","fill"]};

      var Children = ParentNode.childNodes;
      var OrigChildDat = OrigData.childNodes;

      for (var cd = 0; cd < Children.length; cd++){
        var Child = Children[cd];

        var TagName = Child.tagName;
        if (ContainerElements.indexOf(TagName) != -1){
          convertSVG(Child, OrigChildDat[cd])
        } else if (TagName in RelevantStyles){
          var StyleDef = window.getComputedStyle(OrigChildDat[cd]);

          var StyleString = "";
          for (var st = 0; st < RelevantStyles[TagName].length; st++){
            StyleString += RelevantStyles[TagName][st] + ":" + StyleDef.getPropertyValue(RelevantStyles[TagName][st]) + "; ";
          }

          Child.setAttribute("style",StyleString);
        }
      }
    };


  };

  return setupMenu;
}); // End of define
