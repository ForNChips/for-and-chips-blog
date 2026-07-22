/* Article relationship graph for /article-graph/. Nodes = articles; two
   switchable edge sets: cross-references ({{< ref >}}) and shared tags.
   Data comes from the #article-graph-data JSON payload. */
(function () {
  const data = ForceGraph.readData('article-graph-data');
  const container = document.getElementById('article-graph');
  if (!data || !container) return;

  const c = ForceGraph.themeColors();
  const { svg, g, width, height } = ForceGraph.createSvg(container, { ratio: 0.6, minHeight: 520 });

  const nodes    = data.nodes.map(n => Object.assign({}, n));
  const refLinks = ForceGraph.dedupeLinks(data.refLinks);
  const tagLinks = data.tagLinks.slice();

  const truncate = (s, n) => s.length > n ? s.slice(0, n - 1) + '…' : s;

  const linkLayer = g.append('g').attr('class', 'article-graph__links');
  const nodeLayer = g.append('g').attr('class', 'article-graph__nodes');

  const radius = 16;
  const simulation = d3.forceSimulation(nodes)
    .force('charge',    d3.forceManyBody().strength(-280))
    .force('center',    d3.forceCenter(width / 2, height / 2))
    .force('collision', d3.forceCollide().radius(radius + 14));

  const nodeSel = nodeLayer.selectAll('g')
    .data(nodes, d => d.id).join('g')
    .attr('class', 'article-graph-node')
    .style('cursor', 'pointer')
    .call(ForceGraph.dragBehavior(simulation))
    .on('click', function (event, d) {
      if (event.defaultPrevented) return;
      window.location.href = d.url;
    });

  nodeSel.append('circle')
    .attr('r', radius)
    .attr('fill', c.accent)
    .attr('fill-opacity', 0.88)
    .attr('stroke', '#fff')
    .attr('stroke-width', 2);

  nodeSel.append('text')
    .text(d => truncate(d.title, 38))
    .attr('text-anchor', 'middle')
    .attr('dy', radius + 14)
    .attr('font-size', '11px').attr('fill', c.primary)
    .attr('pointer-events', 'none');

  const tooltip = ForceGraph.createTooltip();
  ForceGraph.bindTooltip(nodeSel, tooltip, function (d) {
    const tagText = (d.tags || []).join(', ') || '—';
    const auth    = (d.authors || []).join(', ') || '—';
    return '<strong>' + d.title + '</strong><br>' +
           auth + ' · ' + d.date + '<br>' +
           '<em>' + tagText + '</em>';
  });

  /* Render the chosen edge set and re-run the simulation. */
  function setMode(mode) {
    const active = mode === 'tags' ? tagLinks : refLinks;

    let linkSel = linkLayer.selectAll('line')
      .data(active, d => d.source.id + '|' + d.target.id);
    linkSel.exit().remove();
    linkSel.enter().append('line')
      .attr('stroke', c.secondary)
      .attr('stroke-opacity', 0.5)
      .merge(linkSel)
      .attr('stroke-width', d => Math.max(1, Math.sqrt(d.value || 1) * (mode === 'tags' ? 2.2 : 2.8)));

    simulation
      .force('link', d3.forceLink(active).id(d => d.id)
        .distance(mode === 'tags' ? 140 : 120)
        .strength(0.6))
      .alpha(0.9)
      .restart();
  }

  simulation.on('tick', function () {
    linkLayer.selectAll('line')
      .attr('x1', d => d.source.x).attr('y1', d => d.source.y)
      .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
    nodeSel.attr('transform', d => 'translate(' + d.x + ',' + d.y + ')');
  });

  /* Toggle UI */
  document.querySelectorAll('.article-graph-toggle__btn').forEach(function (btn) {
    btn.addEventListener('click', function () {
      document.querySelectorAll('.article-graph-toggle__btn').forEach(function (b) {
        b.classList.remove('is-active');
        b.setAttribute('aria-selected', 'false');
      });
      btn.classList.add('is-active');
      btn.setAttribute('aria-selected', 'true');
      setMode(btn.dataset.mode);
    });
  });

  setMode('refs');
})();
