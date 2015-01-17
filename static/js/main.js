var colors = {'food':'#fff', 'transportation':'#fff', 'school':'#fff', 'recreation':'#fff', 'vices':'#fff',
'housing':'#fff'}


var data = [4, 8, 15, 16, 23, 42];

var width = $("#maxwidth").width(),
    barHeight = 20;

var x = d3.scale.linear()
    .domain([0, d3.max(data)])
    .range([0, width]);

var chart = d3.select(".chart")
    .attr("width", width)
    .attr("height", barHeight * data.length);

var bar = chart.selectAll("g")
    .data(data)
  .enter().append("g")
    .attr("transform", function(d, i) { return "translate(0," + i * barHeight + ")"; });

bar.append("rect")
    .attr("width", x)
    .attr("height", barHeight - 1);

bar.append("text")
    .attr("x", function(d) { return x(d) - 3; })
    .attr("y", barHeight / 2)
    .attr("dy", ".35em")
    .text(function(d) { return d; });




var n = 6, // number of layers
    m = 200, // number of samples per layer
    stack = d3.layout.stack().offset("wiggle"),
    // stack = d3.layout.stack().offset("expand"),
    // layers1 = stack([[{'x':0,'y':.2 },{'x':1,'y':.4},{'x':2,'y':.5},{'x':3,'y':.1}], [{'x':0,'y':.8 },{'x':1,'y':.6},{'x':2,'y':.5},{'x':3,'y':.9}]]);
    layers0 = stack(d3.range(n).map(function() { return bumpLayer(m); }));
    layers1 = stack(d3.range(n).map(function() { return bumpLayer(m); }));

var width = $("#mainImage").width(),
    height = $("#mainImage").width()*.5;

var x = d3.scale.linear()
    .domain([0, m - 1])
    .range([0, width]);

var y = d3.scale.linear()
    .domain([0, d3.max(layers0.concat(layers1), function(layer) { return d3.max(layer, function(d) { return d.y0 + d.y; }); })])
    .range([height, 0]);

var color = d3.scale.linear()
    .range(["#b6aab4", "#556"]);

var area = d3.svg.area()
    .x(function(d) { return x(d.x); })
    .y0(function(d) { return y(d.y0); })
    .y1(function(d) { return y(d.y0 + d.y); });

var svg = d3.select("#mainImage").append("svg")
    .attr("width", width)
    .attr("height", height);

svg.selectAll("path")
    .data(layers0)
  .enter().append("path")
    .attr("d", area)
    .style("fill", function() { return color(Math.random()); });

function transition() {
  d3.selectAll("path")
      .data(function() {
        var d = layers1;
        layers1 = layers0;
        return layers0 = d;
      })
    .transition()
      .duration(2500)
      .attr("d", area);
}

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
  for (i = 0; i < n; ++i) a[i] = 0;
  for (i = 0; i < 5; ++i) bump(a);



// return [{'x':0,'y':.2 },{'x':1,'y':.3},{'x':2,'y':.5},{'x':3,'y':.5}]
  return a.map(function(d, i) { return {x: i, y: Math.max(0, d)}; });
}
