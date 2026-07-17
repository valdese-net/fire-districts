function InitBurkeFDProximityMap(src) {
	const protocol = new pmtiles.Protocol();
	maplibregl.addProtocol("pmtiles", protocol.tile);
	const PMTILES_URL = src; 
	const p = new pmtiles.PMTiles(PMTILES_URL);
	protocol.add(p);
	const map = new maplibregl.Map({
		container: 'map',
		style: {
			version: 8,
			sources: {
				"fd": {
					type: "vector",
					url: `pmtiles://${PMTILES_URL}`
				}
			},
			layers: [
				{
					"id": "background",
					"type": "background",
					"paint": { "background-color": "#000000" }
				},
				{
					"id": "county",
					"type": "line",
					"source": "fd",
					"source-layer": "burke", 
					"paint": { "line-color": "#ffffff" }
				},
				{
					"id": "district",
					"type": "fill",
					"source": "fd",
					"source-layer": "firedistricts", 
					"paint": { "fill-color": "#888", "fill-opacity":0.4, "fill-outline-color": "white" }
				},
				{
					"id": "parcel",
					"type": "circle",
					"source": "fd",
					"source-layer": "parcels",
					"paint": {"circle-color": ["case",
						["==",["get","FSID_nearestindistrict"],["get","FSID_nearest"]], "green",
						["<",["length", ["get", "FDID"]],1], "#66a",
						["!=",["get","FSID_nearestindistrict"],["get","FSID_nearest"]], "red",
						"white"]
					}
				},
				{
					"id": "station",
					"type": "circle",
					"source": "fd",
					"source-layer": "firestations",
					"paint": { "circle-color": "yellow" }
				},
			]
		},
		center: [-81.65983,35.71655],
		zoom: 10
	});

	map.on('click', function(e) {
		const bbox = [[e.point.x - 1, e.point.y - 1], [e.point.x + 1, e.point.y + 1]];
		const features = map.queryRenderedFeatures(bbox);
		if (!features.length) return;

		const d = [];
		features.forEach((feature) => {
            d.unshift(`<p>${feature.layer.id}<br>${JSON.stringify(feature.properties, null, 2)}</p>`);
		});

		new maplibregl.Popup()
			.setLngLat(e.lngLat)
			.setHTML('<div style="max-height:50vh;overflow:auto">'+d.join('')+'</div>')
			.addTo(map);
	});
}