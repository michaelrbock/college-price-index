var highcatagories = ['food','transportation','school','recreational','vices','housing']
var colors = {'food':'#c16e33', 'transportation':'#3b489a', 'school':'#5b816c', 'recreational':'#694b81', 'vices':'#86963b',
'housing':'#55302c'}


var colorsMain = ['#c16e33','#86963b', '#55302c', '#5b816c', '#694b81','#3b489a']

var maingraphdata = null;
d3.json("https://collegepriceindex.appspot.com/api/categories", function(error, json) {


  maingraphdata = json.data


  var catindexmain = 0;


var n = highcatagories.length, // number of layers
    m = maingraphdata[0].history.length, // number of samples per layer
    stack = d3.layout.stack().offset("wiggle"),
    // stack = d3.layout.stack().offset("expand"),

    layers0 = stack(d3.range(n).map(function() { return bumpLayer(m); }));
    console.log(layers0);




    var width = $("#mainImage").width(),
    height = $("#mainImage").width()*.25;

    var x = d3.scale.linear()
    .domain([0, m - 1])
    .range([0, width]);

    var y = d3.scale.linear()
    .domain([0, d3.max(layers0, function(layer) { return d3.max(layer, function(d) { return d.y0 + d.y; }); })])
    .range([height, 0]);

    var color = d3.scale.linear()
    .range(["#b6aab4", "#556"]);

    var area = d3.svg.area()
    .x(function(d) {
      //console.log(d);
      return x(d.x); })
    .y0(function(d) { return y(d.y0); })
    .y1(function(d) { return y(d.y0 + d.y); });

    var svg = d3.select("#mainImage").append("svg")
    .attr("width", width)
    .attr("height", height);


    svg.selectAll("path")
    .data(layers0)
    .enter().append("path")
    .attr("d", area)
    .style("fill", function(d){



      result = colors[d[0].title];

      return result
    });
    //.style("fill", function() { return color(Math.random()); });

    highcatagories.forEach(function(catagory) {
      smallChartsRender(catagory);
  });

  // Inspired by Lee Byron's test data generator.
  function bumpLayer(n) {



    function bump(a) {
      var x = 1 / (.1 + Math.random()),
      y = 2 * Math.random() - .5,
      z = 10 / (.1 + Math.random());
      for (var i = 0; i < n; i++) {
        var w = (i / n - y) * z;
        a[i] += x * Math.exp(-w * w);
      }
    }

    var a = [], i;
    mainDataDict = maingraphdata[catindexmain];
    // console.log(mainDataDict)



        // console.log(a,i)
        for (i = 0; i < n; ++i) a[i] = maingraphdata[catindexmain].history[i].average;




      // return [{'x':0,'y':.2 },{'x':1,'y':.3},{'x':2,'y':.5},{'x':3,'y':.5}]
    results= a.map(function(d, i) { return {x: i, y: Math.max(0, d),title:maingraphdata[catindexmain].title}; });
    catindexmain += 1;
  // console.log(results)
    return results
  }

});


var smallChartsRender = function(catagory){

  var catagoryid = "#" + catagory + "Chart";




    var format = d3.time.format("%m/%d/%Y");

    var margin = {top: 20, right: 30, bottom: 30, left: 40},
    width = $(catagoryid).width() - margin.left - margin.right,
    height = $(catagoryid).width() - margin.top - margin.bottom;
        // height = height /2;

        var x = d3.time.scale()
        .range([0, width]);

        var y = d3.scale.linear()
        .range([height, 0]);

        var z = d3.scale.category20c();

        var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom")
        .ticks(d3.time.months, 6);

        var yAxis = d3.svg.axis()
        .scale(y)
        .tickFormat(d3.format("$s"))
        .orient("left");

        var stack = d3.layout.stack()
        .offset("zero")
        .values(function(d) { return d.values; })
        .x(function(d) { return d.date; })
        .y(function(d) { return d.value; });

        var nest = d3.nest()
        .key(function(d) { return d.key; });

        var area = d3.svg.area()
        .interpolate("basis")

        .x(function(d) { return x(d.date); })
        .y0(function(d) { return y(d.y0); })
        .y1(function(d) { return y(d.y0 + d.y); });

        var svg = d3.select(catagoryid).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");




          var catindex = 0
          var index = 0;
          maingraphdata.forEach(function(d){


            if (d.title == catagory) {
              catindex = index

            }
            index = index +1;

          });

          data = maingraphdata[catindex].history

          data.forEach(function(d){

            d.date = format.parse(d.start_date);

            d.value = +d.average;




          })





          var layers = stack(nest.entries(data));

          x.domain(d3.extent(data, function(d) { return d.date; }));
          y.domain([0, d3.max(data, function(d) { return d.y0 + d.y; })]);

          svg.selectAll(".layer")
          .data(layers)
          .enter().append("path")
          .attr("class", "layer")
          .attr("d", function(d) { return area(d.values); })
          .style("fill", colors[catagory]);

          svg.append("g")
          .attr("class", "x axis")
          .attr("transform", "translate(0," + height + ")")
          .call(xAxis);

          svg.append("g")
          .attr("class", "y axis")
          .attr("transform", "translate(0,0)")
          .call(yAxis);
        };
