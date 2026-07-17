function InitBurkeFDMap(src) {
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
					"id": "station",
					"type": "circle",
					"source": "fd",
					"source-layer": "firestations",
					"paint": { "circle-color": "yellow" }
				},
				{
					"id": "goodparcel",
					"type": "circle",
					"source": "fd",
					"source-layer": "parcels",
					"filter": ["==",["get","FSID_nearestindistrict"],["get","FSID_nearest"]],
					"paint": { "circle-color": "green" }
				},
				{
					"id": "badparcel",
					"type": "circle",
					"source": "fd",
					"source-layer": "parcels",
					"filter": ["!=",["get","FSID_nearestindistrict"],["get","FSID_nearest"]],
					"paint": { "circle-color": "red" }
				},
			]
		},
		center: [-81.65983,35.71655],
		zoom: 10
	});
}