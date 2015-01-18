var highcatagories = ['food','transportation','school','recreational','vices','housing']
var colors = {'food':'#c16e33', 'transportation':'#3b489a', 'school':'#5b816c', 'recreational':'#694b81', 'vices':'#86963b',
'housing':'#55302c'}






highcatagories.forEach(function(catagory){

    var catagoryid = "#" + catagory + "Chart";
    // console.log(catagoryid)



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



    d3.json("https://collegepriceindex.appspot.com/api/categories/", function(error, json) {
          // if (error) return console.warn(error);
          // console.log(json)
        var catindex = 0
        var index = 0;
        json.data.forEach(function(d){


            if (d.title == catagory) {
                catindex = index

            }
            index = index +1;

          });

          data = json.data[catindex].history

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
    });
});
