/* Co-authorship network for /collab/. Nodes = authors (size ∝ article count,
   colour ∝ role), edges = co-authored articles. Data comes from the
   #collab-graph-data JSON payload emitted by the template. */
(function () {
  const raw = ForceGraph.readData('collab-graph-data');
  const container = document.getElementById('collab-graph');
  if (!raw || !container) return;

  const links = ForceGraph.dedupeLinks(raw.links);
  const nodes = raw.nodes.map(n => Object.assign({}, n));

  const c = ForceGraph.themeColors();
  const roleColors = {
    'founder':         c.accent,
    'researcher':      '#3B82F6',
    'practitioner':    '#10B981',
    'law enforcement': '#1E3A5F',
    'contributor':     c.secondary,
  };
  const nodeColor  = d => roleColors[(d.role || '').toLowerCase()] || c.secondary;
  const nodeRadius = d => Math.max(20, Math.sqrt((d.count || 0) + 1) * 13);

  const { svg, g, width, height } = ForceGraph.createSvg(container, { ratio: 0.55, minHeight: 440 });

  const simulation = d3.forceSimulation(nodes)
    .force('link', d3.forceLink(links).id(d => d.id).distance(130))
    .force('charge', d3.forceManyBody().strength(-350))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(d => nodeRadius(d) + 12));

  const link = g.append('g').attr('class', 'collab-links')
    .selectAll('line').data(links).join('line')
    .attr('stroke', c.secondary)
    .attr('stroke-opacity', 0.45)
    .attr('stroke-width', d => Math.max(1, Math.sqrt(d.value) * 2.5));

  const node = g.append('g').attr('class', 'collab-nodes')
    .selectAll('g').data(nodes).join('g')
    .attr('class', 'collab-node')
    .call(ForceGraph.dragBehavior(simulation));

  node.append('circle')
    .attr('r', nodeRadius)
    .attr('fill', nodeColor)
    .attr('fill-opacity', 0.88)
    .attr('stroke', '#fff')
    .attr('stroke-width', 2.5);

  node.append('text')
    .text(d => d.count || 0)
    .attr('text-anchor', 'middle').attr('dy', '0.35em')
    .attr('font-size', '13px').attr('font-weight', '700')
    .attr('fill', '#fff').attr('pointer-events', 'none');

  node.append('text')
    .text(d => d.name)
    .attr('text-anchor', 'middle')
    .attr('dy', d => nodeRadius(d) + 15)
    .attr('font-size', '11px').attr('fill', c.primary)
    .attr('pointer-events', 'none');

  const tooltip = ForceGraph.createTooltip();
  ForceGraph.bindTooltip(node, tooltip, d =>
    '<strong>' + d.name + '</strong><br>' +
    d.role + ' · ' + d.count + ' article' + (d.count !== 1 ? 's' : ''));

  simulation.on('tick', function () {
    link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
        .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
    node.attr('transform', d => 'translate(' + d.x + ',' + d.y + ')');
  });

  /* Legend */
  const legend = svg.append('g').attr('transform', 'translate(16, 16)');
  Object.entries(roleColors).forEach(function (entry, i) {
    const lg = legend.append('g').attr('transform', 'translate(0,' + (i * 22) + ')');
    lg.append('circle').attr('r', 7).attr('cx', 7).attr('cy', 7)
      .attr('fill', entry[1]).attr('fill-opacity', 0.88);
    lg.append('text').text(entry[0].charAt(0).toUpperCase() + entry[0].slice(1))
      .attr('x', 20).attr('y', 7).attr('dy', '0.35em')
      .attr('font-size', '11px').attr('fill', c.primary);
  });
})();
