define('slider',['d3','tooltip'], function(d3,tooltip){

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

  function sliderMenu(container,config,network){

    // get config values
    var pastDelta = 0;
    var futureDelta = 0;
    var aggregationDelta = 0;

    // dont show aggrigation and lookout
    var aggregationShow = false;
    var lookoutShow = false;

    // initialize timer
    var timer = null;

    // tooltip for mouseover functionality
    // implemented in tooltip.js
    var myTooltip = tooltip('menu-tooltip');

    // create menu bar which contains the control widgets
    var menuBar = d3.select(container)
        .append('div')
        .attr('class','pp_container')
        .attr('id','#pp_slider');

    // container for the buttons
    var controlBar = menuBar
        .append('div')
        .attr('class','controls')
        .attr('id','#controls');

    // container of the animation buttons
    var animationControl = d3.create('div')
        .attr('class','control')
        .attr('id','animation')
        .on('mouseover', function () {
          myTooltip.showTooltip(getTooltip(config,'animation'), d3.event);})
        .on("mouseout",function () {
          myTooltip.hideTooltip();});

    // save svg button
    var playBtn = d3.create('button')
        .text('Play');

    // assign button to the animation cotrole
    animationControl.append(function(){ return playBtn.node(); });

    // container of the aggregation buttons
    var aggregationControl = d3.create('div')
        .attr('class','control pp_vl')
        .attr('id','aggregation')
        .on('mouseover', function () {
          myTooltip.showTooltip(getTooltip(config,'aggregation'), d3.event);})
        .on("mouseout",function () {
          myTooltip.hideTooltip();});

    // make button to enable aggregation of time steps
    var aggregationBtn = d3.create('button')
        .text('Aggregate')
        .classed('active', false);

    // make button to enable lookouts
    var lookoutBtn = d3.create('button')
        .text('Lookout')
        .classed('active', false);

    // assign button to the aggregation cotrole
    aggregationControl.append(function(){ return aggregationBtn.node(); });

    // assign button to the aggregation cotrole
    aggregationControl.append(function(){ return lookoutBtn.node(); });

    // assign controls to widget if enabled
    if (config.widgets.animation.enabled === true){
      controlBar.append(function(){ return animationControl.node(); });};

    // assign controls to widget if enabled
    if (config.widgets.aggregation.enabled === true){
      controlBar.append(function(){ return aggregationControl.node(); });};

    ///////////////// generate slider /////////////////////

    var formatInt = d3.format(",.0f");
    var unit = config.animation.unit || "seconds";
    var formatDateIntoMillisecond = d3.timeFormat(".%L"),
        formatDateIntoSecond = d3.timeFormat("%M:%S"),
        formatDateIntoMinute = d3.timeFormat("%I:%M"),
        formatDateIntoHour = d3.timeFormat("%I %p"),
        formatDateIntoDay = d3.timeFormat("%a %d"),
        formatDateIntoWeek = d3.timeFormat("%b %d"),
        formatDateIntoMonth = d3.timeFormat("%B"),
        formatDateIntoMonthYear = d3.timeFormat("%b %Y"),
        formatDateIntoYear = d3.timeFormat("%Y");

    var formatTickDate = formatDateIntoSecond;
    var formatDate = formatDateIntoSecond;

    if (unit === "seconds"){
      formatTickDate = formatDateIntoSecond;
      formatDate = formatDateIntoSecond;
    } else if (unit === "minutes"){
      formatTickDate = formatDateIntoMinute;
      formatDate = formatDateIntoMinute;
    }else if (unit === "days"){
      formatTickDate = formatDateIntoDay;
      formatDate = formatDateIntoDay;
    }else if (unit === "weeks"){
      formatTickDate = formatDateIntoWeek;
      formatDate = formatDateIntoWeek;
    }else if (unit === "months"){
      formatTickDate = formatDateIntoMonth;
      formatDate = formatDateIntoMonth;
    }else if (unit === "years"){
      formatTickDate = formatDateIntoMonthYear;
      formatDate = formatDateIntoYear;
    }

    var startDate = new Date(config.animation.start),
        endDate = new Date(config.animation.end);

    // devine margin and width of the slider
    var margin = {top:0, right:50, bottom:0, left:50},
        width = 600 - margin.left - margin.right,
        height = 80 - margin.top - margin.bottom;

    // add svg to the menu bar
    var svg = menuBar
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom);
      //.style("background-color","#f6f7ba");

    var moving = false;
    var currentValue = 0;
    var targetValue = width;
    var timeSteps = config.animation.steps || 10;

    // convert time steps (e.g. 0,1,2,...) into date values
    var t = d3.scaleTime()
        .domain([startDate, endDate])
        .range([0, targetValue])
        .clamp(true);

    // convert time steps (e.g. 0,1,2,...) into px values
    var x = d3.scaleLinear()
        .domain([0, timeSteps])
        .range([0,targetValue])
        .clamp(true);

    // create slider object
    var slider = svg.append("g")
        .attr("class", "slider")
        .attr("transform", "translate(" + margin.left + "," + height/2 + ")");

    // make track of the slider
    slider.append("line")
      .attr("class", "track")
      .attr("x1", x.range()[0])
      .attr("x2", x.range()[1])
      .select(function() {
        return this.parentNode.appendChild(this.cloneNode(true)); })
      .attr("class", "track-inset");

    // make a line for the past records
    var pastLine = d3.create("svg").append('line')
        .attr("class", "track-past")
        .attr("x1", 0)
        .attr("x2", 0);

    // make a line for the future records
    var futureLine = d3.create("svg").append("line")
        .attr("class", "track-future")
        .attr("x1", x(aggregationDelta))
        .attr("x2", x(aggregationDelta)+x(futureDelta));

    // make a line for the aggregated time steps
    var aggregationLine = d3.create("svg").append("line")
        .attr("class", "track-aggregation")
        .attr("x1", 0)
        .attr("x2", x(aggregationDelta));


    // append lines to the slider
    slider.append(function(){ return pastLine.node(); });
    slider.append(function(){ return futureLine.node(); });//};
    slider.append(function(){ return aggregationLine.node(); });//};


    // add ticks to the slider
    slider.insert("g", ".track-overlay")
      .attr("class", "ticks")
      .attr("transform", "translate(0," + 18 + ")")
      .selectAll("text")
      .data(x.ticks(10))
      .enter()
      .append("text")
      .attr("x", x)
      .attr("y", 10)
      .attr("text-anchor", "middle")
      .text(function(d) { return formatTickDate(t.invert(x(d))); });

    // add handler to the slider
    var handle = slider.insert("circle", ".track-overlay")
        .attr("class", "handle")
        .attr("cx",0)
        .attr("r", 9)
        .call(d3.drag()
              .on("start.interrupt", function() { slider.interrupt(); })
              .on("start drag", function() {
                currentValue = d3.event.x;
                update(x.invert(currentValue));
              })
           );


    // add handler to the slider
    var pastHandle = d3.create("svg").append("circle")
        .attr("class", "handle")
        .attr('id','pastHandle')
        .attr("r", 6)
        .attr("transform", "translate(-8,8)")
        .call(d3.drag()
              .on("drag", function() {
                pastUpdate(x.invert(d3.event.x));
              })
             );


    // add handler to the slider
    var futureHandle = d3.create("svg").append("circle")
        .attr("class", "handle")
        .attr('id','futureHandle')
        .attr("r", 6)
        .attr("cx",x(aggregationDelta)+x(futureDelta))
        .attr("transform", "translate(8,8)")
        .call(d3.drag()
              .on("drag", function() {
                futureUpdate(x.invert(d3.event.x));
              })
             );


    // add handler to the slider
    var aggregationHandle = d3.create("svg").append("circle")
        .attr("class", "handle")
        .attr('id','aggregationHandle')
        .attr("r", 6)
        .attr("cx",x(aggregationDelta))
        .attr("transform", "translate(8,-8)")
        .call(d3.drag()
              .on("drag", function() {
                aggregationUpdate(x.invert(d3.event.x));
              })
             );

    // show data if enabled
    if (lookoutShow === true){
      slider.append(function(){ return pastHandle.node(); });
      slider.append(function(){ return futureHandle.node(); });};

    if (aggregationShow === true){
      slider.append(function(){ return aggregationHandle.node(); });};


    // add lable showing current time stamp
    var label = slider.append("text")
        .attr("id", "pp_slider_label")
        .attr("text-anchor", "middle")
        .text(formatDate(startDate))
        .attr("transform", "translate(0," + (-20) + ")");

    ///////////////// generate button actions /////////////////////

    playBtn
      .on("click", function() {
        var button = d3.select(this);
        if (button.text() == "Pause") {
          moving = false;
          //clearInterval(timer);
          timer.stop()
          // timer = 0;
          button.text("Play");
        } else {
          moving = true;
          // wait some time e.g. 1000 = 1000 ms = 1 sec
          timer = d3.interval(function(){step()},
                              config.widgets.animation.speed || 100);
          button.text("Pause");
        }
        //console.log("Slider moving: " + moving);
      });

    aggregationBtn
        .on('click', function () {
          var button = d3.select(this);

          if (aggregationShow === false){
            button.classed('active', true);
            aggregationShow = true;
            aggregationDelta = config.widgets.aggregation.aggregation || 0;
            slider.append(function(){ return aggregationHandle.node(); });

          } else {
            button.classed('active', false);
            aggregationShow = false;
            aggregationDelta = 0;
            d3.select('#aggregationHandle').remove();
          };
          update(x.invert(currentValue));
        });

    lookoutBtn
        .on('click', function () {
          var button = d3.select(this);

          if (lookoutShow === false){
            button.classed('active', true);
            lookoutShow = true;
            pastDelta = config.widgets.aggregation.past || 0;
            futureDelta = config.widgets.aggregation.future || 0;
            slider.append(function(){ return pastHandle.node(); });
            slider.append(function(){ return futureHandle.node(); });

          } else {
            button.classed('active', false);
            lookoutShow = false;
            pastDelta = 0;
            futureDelta = 0;
            d3.select('#pastHandle').remove();
            d3.select('#futureHandle').remove();
          };
          update(x.invert(currentValue));
        });


    ///////////////// generate iterative functions /////////////////////

    function step() {
      update(x.invert(currentValue));
      currentValue = currentValue + (targetValue/timeSteps);

      if (currentValue+x(aggregationDelta) > targetValue) {
        moving = false;
        currentValue = 0;
        // stop after time is max
        timer.stop()
        //clearInterval(timer);
        // timer = 0;
        playBtn.text("Play");
      }
    };


    function update(value) {
      // update position and text of label according to slider scale
      handle.attr("cx", x(value));

      if (x(value)>x(pastDelta)){
        pastHandle.attr("cx", x(value)-x(pastDelta));
        pastLine.attr('x1',x(value)-x(pastDelta));
      } else{
        pastHandle.attr("cx", 0);
        pastLine.attr('x1',0);
      };

      if ((x(value)+x(aggregationDelta))<width){
      aggregationHandle.attr("cx", x(value)+x(aggregationDelta));
      aggregationLine.attr('x2',x(value)+x(aggregationDelta));
      } else{
        aggregationHandle.attr("cx", width);
        aggregationLine.attr('x2',width);
        futureLine.attr('x2',width);
      };


      if ((x(value)+x(aggregationDelta)+x(futureDelta))<width){
      futureHandle.attr("cx", x(value)+x(aggregationDelta)+x(futureDelta));
      futureLine.attr('x2',x(value)+x(aggregationDelta)+x(futureDelta));
      } else{
        futureHandle.attr("cx", width);
        futureLine.attr('x2',width);
      };

      label
        .attr("x", x(value))
        .text(formatDate(t.invert(x(value))));

      pastLine.attr('x2',x(value));
      if ((x(value)+x(aggregationDelta))<width){
        futureLine.attr('x1',x(value)+x(aggregationDelta));
      }else{
        futureLine.attr('x1',width);
      };
      aggregationLine.attr('x1',x(value));

      var newTime = {
        past : parseInt(formatInt(x.invert(pastHandle.attr("cx")))),
        time : parseInt(formatInt(value)),
        aggregated : parseInt(formatInt(value+aggregationDelta)),
        future : parseInt(formatInt(x.invert(futureHandle.attr("cx"))))
      };

      // update the network
      network.updateTime(newTime);
    }

    function pastUpdate(value) {
      var delta = parseInt(formatInt(value))
          - parseInt(formatInt(x.invert(handle.attr('cx'))));
      if (delta <= 0 && x(value) < handle.attr('cx')){
        pastDelta = Math.abs(delta);
        pastHandle.attr("cx", x(value));
        pastLine.attr('x1',x(value));
        update(x.invert(currentValue));
      };
    };

    function futureUpdate(value) {
      var delta = parseInt(formatInt(value))
          - parseInt(formatInt(x.invert(aggregationHandle.attr('cx'))));
      if (delta >= 0 && x(value) > handle.attr('cx')){
        futureDelta = Math.abs(delta);
        futureHandle.attr("cx", x(value));
        futureLine.attr('x2',x(value));
        update(x.invert(currentValue));
      };
    };


    function aggregationUpdate(value) {
      var delta = parseInt(formatInt(value))
          - parseInt(formatInt(x.invert(handle.attr('cx'))));
      if (delta >= 0 && x(value) > handle.attr('cx')){
        aggregationDelta = Math.abs(delta);
        aggregationHandle.attr("cx", x(value));
        aggregationLine.attr('x2',x(value));

        if ((x(value)+x(futureDelta))<width){
          futureHandle.attr("cx", x(value)+x(futureDelta));
          futureLine.attr('x2',x(value)+x(futureDelta));
        } else{
          futureHandle.attr("cx", width);
          futureLine.attr('x2',width);
        };

        futureLine.attr('x1',x(value));

        update(x.invert(currentValue));
      };
    };

  }; // End of sliderMenu

  return sliderMenu;
}); // End of define
