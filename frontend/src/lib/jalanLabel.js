const UTAMA = new Set(["trunk", "primary", "secondary", "tertiary"]);

/** Sambung potongan jalan bernama hanya untuk label; graf routing tetap utuh.
 * Ruas pendek antarsimpang tidak cukup panjang untuk nama jalan pada zoom awal.
 * Duplikat arah dibuang, lalu rantai dengan nama sama disambung sampai cabang.
 */
export function buatLabelJalan(jaringan) {
  const groups = new Map();
  for (const f of jaringan.features ?? []) {
    const nama = f.properties?.nama?.trim();
    if (!nama || f.geometry?.type !== "LineString" || f.geometry.coordinates.length < 2) continue;
    const utama = UTAMA.has(f.properties.jenis);
    const key = `${utama}:${nama}`;
    if (!groups.has(key)) groups.set(key, { nama, utama, edges: [], seen: new Set() });
    const group = groups.get(key);
    const coords = f.geometry.coordinates;
    const a = coords.map((p) => p.join(",")).join(";");
    const b = [...coords].reverse().map((p) => p.join(",")).join(";");
    const signature = a < b ? a : b;
    if (!group.seen.has(signature)) { group.seen.add(signature); group.edges.push(coords); }
  }
  const features = [];
  for (const { nama, utama, edges } of groups.values()) {
    const nodes = new Map();
    edges.forEach((coords, id) => {
      for (const p of [coords[0], coords.at(-1)]) {
        const key = p.join(",");
        if (!nodes.has(key)) nodes.set(key, []);
        nodes.get(key).push(id);
      }
    });
    const used = new Set();
    const walk = (start, first) => {
      let node = start, id = first;
      const line = [];
      while (!used.has(id)) {
        used.add(id);
        const edge = edges[id];
        const points = edge[0].join(",") === node ? edge : [...edge].reverse();
        line.push(...(line.length ? points.slice(1) : points));
        node = points.at(-1).join(",");
        const next = nodes.get(node);
        if (next.length !== 2) break;
        id = next.find((candidate) => !used.has(candidate));
        if (id === undefined) break;
      }
      features.push({ type: "Feature", properties: { nama, label: nama.replace(/^Jalan\s+/i, "Jl. "), utama },
        geometry: { type: "LineString", coordinates: line } });
    };
    for (const [node, ids] of nodes) {
      if (ids.length !== 2) for (const id of ids) if (!used.has(id)) walk(node, id);
    }
    edges.forEach((edge, id) => { if (!used.has(id)) walk(edge[0].join(","), id); });
  }
  return { type: "FeatureCollection", features };
}
