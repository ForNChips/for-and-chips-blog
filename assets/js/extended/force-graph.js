/* Shared D3 force-directed-graph helpers.
 *
 * Used by collab-graph.js (co-authorship) and article-graph.js (article
 * relationships). Keeps the boilerplate they both need — theme colours,
 * responsive SVG + zoom, drag behaviour, link de-duplication, hover
 * tooltip, JSON payload reading — in one place. Each graph supplies its
 * own node/link rendering on top.
 *
 * Requires D3 v7 to be loaded first.
 */
const ForceGraph = (function () {
  /* Resolve the site's CSS custom properties (with fallbacks) so graph
     colours track the active theme. */
  function themeColors() {
    const s = getComputedStyle(document.documentElement);
    const v = (name, fallback) => s.getPropertyValue(name).trim() || fallback;
    return {
      accent:    v('--accent', '#C42B0C'),
      secondary: v('--secondary', '#6B5232'),
      entry:     v('--entry', '#F7F5F0'),
      primary:   v('--primary', '#1A1204'),
    };
  }

  /* Append a responsive <svg> + inner <g>, wired for scroll-zoom / pan.
     opts: { ratio, minHeight, scaleExtent } */
  function createSvg(container, opts) {
    opts = opts || {};
    const width  = container.offsetWidth || 800;
    const height = Math.max(opts.minHeight || 440, Math.round(width * (opts.ratio || 0.55)));
    const svg = d3.select(container).append('svg')
      .attr('width', '100%')
      .attr('height', height)
      .attr('viewBox', '0 0 ' + width + ' ' + height)
      .attr('preserveAspectRatio', 'xMidYMid meet');
    const g = svg.append('g');
    svg.call(d3.zoom().scaleExtent(opts.scaleExtent || [0.25, 4]).on('zoom', function (event) {
      g.attr('transform', event.transform);
    }));
    return { svg: svg, g: g, width: width, height: height };
  }

  /* Standard "pin while dragging" behaviour for a force simulation. */
  function dragBehavior(simulation) {
    return d3.drag()
      .on('start', function (event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x; d.fy = d.y;
      })
      .on('drag', function (event, d) { d.fx = event.x; d.fy = event.y; })
      .on('end', function (event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null; d.fy = null;
      });
  }

  /* Collapse A→B and B→A into one undirected edge, counting weight. */
  function dedupeLinks(rawLinks) {
    const map = {};
    rawLinks.forEach(function (l) {
      const key = [l.source, l.target].sort().join('|||');
      map[key] = (map[key] || 0) + 1;
    });
    return Object.entries(map).map(function (e) {
      const parts = e[0].split('|||');
      return { source: parts[0], target: parts[1], value: e[1] };
    });
  }

  function createTooltip() {
    return d3.select('body').append('div').attr('class', 'collab-tooltip').style('opacity', 0);
  }

  /* Wire mouse hover on a selection to show `htmlFn(d)` in the tooltip. */
  function bindTooltip(selection, tooltip, htmlFn) {
    selection
      .on('mouseenter', function (event, d) {
        tooltip.transition().duration(150).style('opacity', 1);
        tooltip.html(htmlFn(d))
          .style('left', (event.pageX + 12) + 'px')
          .style('top',  (event.pageY - 28) + 'px');
      })
      .on('mousemove', function (event) {
        tooltip.style('left', (event.pageX + 12) + 'px').style('top', (event.pageY - 28) + 'px');
      })
      .on('mouseleave', function () {
        tooltip.transition().duration(200).style('opacity', 0);
      });
  }

  /* Read a <script type="application/json"> payload by element id. */
  function readData(id) {
    const el = document.getElementById(id);
    if (!el) return null;
    try { return JSON.parse(el.textContent); } catch (e) { return null; }
  }

  return {
    themeColors:  themeColors,
    createSvg:    createSvg,
    dragBehavior: dragBehavior,
    dedupeLinks:  dedupeLinks,
    createTooltip: createTooltip,
    bindTooltip:  bindTooltip,
    readData:     readData,
  };
})();
