// For any third party dependencies, like jQuery, place them in the lib folder.

// Configure loading modules from the lib directory,
// except for 'app' ones, which are in a sibling
// directory.
require.config({
  paths: {
    d3: ['https://d3js.org/d3.v5.min',
         //If the online location fails, load from this location
         'lib/d3.min.js']
  }
});

// Start loading the main app file. Put all of
// your application logic in there.
require(['d3','tooltip','network','widgets','slider'], function(d3,tooltip,network,widgets,slider){
  function run(config){

    // initialize network
    var myNetwork = network(config);

    function display(data) {
      myNetwork('#pathpy', data);
    };

    // load data and show network
    d3.json('data/network.json').then(display);

    // load widgets
    widgets('#pathpy',config,myNetwork);

    // load slider
    if (config.temporal === true){
      slider('#pathpy',config,myNetwork);};

  };

  // load config and start the program
  d3.json('config.json').then(run);
});
