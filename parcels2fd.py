from osgeo import ogr,osr
import lib.debug as debug
import os, csv
import lib.config as config

if not os.path.exists(config.src_burkefd_geojson):
	print(f"Generating {config.src_burkefd_geojson} from {config.src_firedistricts_shapefile}")
	# create a geojson of the Burke County Fire Districts, fixing the FDID for the one that we know is wrong
	# the data is missing fire district Carbon City, has wrong FDID for one of the districts, and is old, but it is what the state is providing
	os.system(f"ogr2ogr -makevalid -where \"fdcounty='Burke' and FDID LIKE '%'\" -f GeoJSON -t_srs EPSG:4326 /vsigzip/./_fd.gz /vsizip/{config.src_firedistricts_shapefile} NC_Fire_Districts")
	# FD '06361' => '01277': the ncone map is wrong, burke has no fire district with fdid 06361, it should be 01277
	os.system(f"zcat ./_fd.gz | sed 's/\"FDID\": \"06361\"/\"FDID\": \"01277\"/' |  gzip -c > {config.src_burkefd_geojson}")
	os.system(f"rm ./_fd.gz")

target_srs = osr.SpatialReference()
target_srs.ImportFromEPSG(4326)

parcelPts = ogr.Open(f'/vsizip/{config.src_parcelcentroids_shapefile}')
parcelptLayer = parcelPts.GetLayer()
xparcelpt = osr.CoordinateTransformation(parcelptLayer.GetSpatialRef(), target_srs)

fdShapes = ogr.Open(f'/vsigzip/{config.src_burkefd_geojson}')
fdLayer = fdShapes.GetLayer()
xfd = osr.CoordinateTransformation(fdLayer.GetSpatialRef(), target_srs)

class ParcelPoint:
	__slots__ = ['id', 'val', 'pt', 'fd']
	def __init__(self, l: ogr.Feature, p: tuple[float, float]):
		self.id = l.GetField('NPARNO')
		self.val = float(l.GetField('PARVAL')) if l.GetField('PARVAL') else 0.0
		self.pt = p
		self.fd = None

class FireDistrict:
	def __init__(self, id: str, name: str):
		self.id = id
		self.name = name
		self.parcels = []

firedistricts = {}
parcels = {}

for ppt in parcelptLayer:
	pt = ppt.GetGeometryRef()
	if not pt or not pt.IsValid(): continue
	pt.Transform(xparcelpt)
	# latlng = (pt.GetX(), pt.GetY())
	newparcel = ParcelPoint(ppt, (pt.GetX(), pt.GetY()))
	parcels[newparcel.id] = newparcel

for fd in fdLayer:
	fd_id = fd.GetField("FDID")
	if fd_id is None: continue

	fd_name = fd.GetField("firedepart")
	geo = fd.GetGeometryRef()

	if not geo or not geo.IsValid():
		print(f"Warning: Fire district geometry is missing. Skipping this feature. {fd_id}: {fd_name}")
		debug.print_geometry_stats(geo)
		continue  # Skip if geometry is missing

	print(f'Processing {fd_id}:{fd_name}')
	geo.Transform(xfd)
	if fd_id in firedistricts:
		firedistrict = firedistricts[fd_id]
	else:
		firedistrict = FireDistrict(fd_id, fd_name)
		firedistricts[fd_id] = firedistrict

	for parcel in parcels.values():
		if parcel.fd is not None: continue

		pt = ogr.Geometry(ogr.wkbPoint)
		pt.AddPoint(parcel.pt[0], parcel.pt[1])

		#if geo.Intersects(pt):
		if geo.Contains(pt):
			if parcel.fd is None:
				parcel.fd = fd_id
				firedistrict.parcels.append(parcel)
			elif parcel.fd != fd_id:
				print(f"Warning: Parcel {parcel.id} already assigned to FD {parcel.fd}. Now also intersects FD {fd_id}: {fd_name}.")

firedistricts = dict(sorted(firedistricts.items()))
parcels = dict(sorted(parcels.items()))

with open(f"{config.src_datafolder}/burkefd.csv", "w", newline='') as out:
	writer = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
	writer.writerow(["FDID", "FDNAME"])
	for fd_id, firedistrict in firedistricts.items():
		writer.writerow([fd_id, firedistrict.name])

with open(f"{config.src_datafolder}/parcel2fd.csv", "w", newline='') as out:
	writer = csv.writer(out, quoting=csv.QUOTE_MINIMAL)
	writer.writerow(["NPARNO", "PARVAL", "FDID", "lat", "lng"])
	for parcel in parcels.values():
		writer.writerow([parcel.id, parcel.val, parcel.fd, f"{parcel.pt[0]:.6f}", f"{parcel.pt[1]:.6f}"])