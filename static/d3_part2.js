
// constants
var geo_width = 960,
    geo_height = 700,
    map_height = 600,
    legend_top_margin = 50,
    geo_buckets = 9,
    geo_legendElementWidth = ((geo_width - 200) / geo_buckets);

// data structures we will use
var fipsToSent = d3.map();
var fipsToName = d3.map();

queue()
    .defer(d3.json, "/static/data/us.json")
    .defer(d3.tsv, "/static/data/part2.tsv", function(d) {
        fipsToSent.set(d.id, +d.sent);
        fipsToName.set(d.id, d.name);
    })
    .await(ready);

// helper function
function toFixed(value, precision) {
    var precision = precision || 0,
    neg = value < 0,
    power = Math.pow(10, precision),
    value = Math.round(value * power),
    integral = String((neg ? Math.ceil : Math.floor)(value / power)),
    fraction = String((neg ? -value : value) % power),
    padding = new Array(Math.max(precision - fraction.length, 0) + 1).join('0');

    return precision ? integral + '.' +  padding + fraction : integral;
}

function ready(error, us) {

    // sanity check that d3 is working
//    var data = [4, 8, 15, 16, 23, 42];
//
//    var x = d3.scale.linear()
//        .domain([0, d3.max(data)])
//        .range([0, 420]);
//
//    d3.select(".chart")
//        .selectAll("div")
//        .data(data)
//        .enter().append("div")
//        .style("width", function(d) { return x(d) + "px"; })
//        .text(function(d) { return d; });
    // end of sanity check

    // tooltip stuff
    /* Initialize tooltip */
    var tip = d3.tip().attr('class', 'd3-tip').html(function(d) {
        var county_name = fipsToName.get(d.id);
        if (county_name) {
            return county_name;
        }
        else {
            return d.id;
        }
    });

    var svg = d3.select("#country_chart").append("svg")
        .attr("width", geo_width)
        .attr("height", geo_height);

    /* Invoke the tip in the context of your visualization */
    svg.call(tip);

    var sent_max = d3.max(fipsToSent.values());
    console.log("sent_max: " + sent_max);

    var quantize = d3.scale.quantize()
        .domain([0, sent_max])
        .range(d3.range(geo_buckets).map(function(i) { return "q" + i + "-9"; }));

    var projection = d3.geo.albersUsa()
        .scale(1280)
        .translate([geo_width / 2, map_height / 2]);

    var path = d3.geo.path()
        .projection(projection);

    svg.append("g")
        .attr("class", "counties")
        .selectAll("path")
        .data(topojson.feature(us, us.objects.counties).features)
        .enter().append("path")
        .attr("class", function(d) {
            var sent = fipsToSent.get(d.id);
            // if there was not enough data make it a special color
            if (sent == 0) {
                return "not-enough-data"
            }
            // else color by the quantize scale
            else {
                return quantize(sent);
            }
        })
        .attr("d", path)
        .on('mouseover', tip.show)
        .on('mouseout', tip.hide);

    svg.append("path")
        .datum(topojson.mesh(us, us.objects.states, function(a, b) { return a !== b; }))
        .attr("class", "states")
        .attr("d", path);

    var legend_range = quantize.range();
    legend_range.push("not-enough-data");

    var legend = svg.selectAll(".legend")
        .data(legend_range)
        .enter().append("g")
        .attr("class", "legend");

    console.log("quantize");
    console.log(quantize.range());

    var legendMargin = 0;
    console.log("legendElementWidth: " + geo_legendElementWidth);

    legend.append("rect")
        .attr("x", function(d, i) { return legendMargin + geo_legendElementWidth * i; })
        .attr("y", map_height+legend_top_margin)
        .attr("width", geo_legendElementWidth)
        .attr("height", 20)
        .attr("class", function(d,i) {
            return d;
        });

    legend.append("text")
        .attr("class", "mono")
        .text(function(d) {
           if (d == "not-enough-data") {
               return "not enough data in county"
           }
           else {
                var input_quantile = quantize.invertExtent(d);
                console.log(input_quantile);
                return "<= " + toFixed(input_quantile[1], 2);
           }
        })
        .attr("x", function(d, i) { return legendMargin + geo_legendElementWidth * i + 15; })
        .attr("y", map_height + legend_top_margin + 45);
}

