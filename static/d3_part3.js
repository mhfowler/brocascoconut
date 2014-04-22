
// constants
var k_width = 960,
    k_height = 700;

queue()
    .defer(d3.json, "/static/data/graph4.json")
    .await(ready);


function ready(error, graph_data) {

    // tooltip stuff
    /* Initialize tooltip */
    var tip = d3.tip().attr('class', 'd3-tip').html(function(d) {
        return d.screen_name;
    });

    var svg = d3.select("#force_graph").append("svg")
        .attr("width", k_width)
        .attr("height", k_height);

    /* call tooltip */
    svg.call(tip);

    // colors
    var color = d3.scale.category20();

    var force = d3.layout.force()
        .gravity(.05)
        .distance(100)
        .charge(-100)
        .size([k_width, k_height])
        .nodes(graph_data.nodes)
        .links(graph_data.links)
        .start();

    var link = svg.selectAll(".link")
        .data(graph_data.links)
        .enter().append("line")
        .attr("class", "link");

    var node = svg.selectAll(".node")
        .data(graph_data.nodes)
        .enter().append("g")
        .attr("class", "node")
        .call(force.drag);

    node.append("text")
        .attr("dx", 12)
        .attr("dy", ".35em")
        .text(function(d) { return d.name });

    node.append("circle")
        .attr("class", "node")
        .attr("r", function(d) {
            return d.size;
        })
        .style("fill", function(d) { return color(d.group); })
        .on('mouseover', tip.show)
        .on('mouseout', tip.hide)
        .call(force.drag);


    force.on("tick", function() {
        link.attr("x1", function(d) { return d.source.x; })
            .attr("y1", function(d) { return d.source.y; })
            .attr("x2", function(d) { return d.target.x; })
            .attr("y2", function(d) { return d.target.y; });
        node.attr("transform", function(d) { return "translate(" + d.x + "," + d.y + ")"; });
    });

}

