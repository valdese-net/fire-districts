
class FireDistrict:
	def __init__(self, id: str, name: str):
		self.FDID = id
		self.name = name
		self.stations = []
		self.parcels = 0
		self.parcelsWithCloserFS = 0
		self.propertyVal = 0.0
		self.propertyValWithCloserFS = 0.0

	def initFromCSV(self, row: dict):
		self.FDID = row['FDID']
		self.name = row['FDNAME']
		self.stations = int(row['STATIONS'])
		self.parcels = int(row['PARCELS'])
		self.propertyVal = float(row['PROPERTYVAL']) if row['PROPERTYVAL'] else 0.0
		self.parcelsWithCloserFS = int(row['PARCELS_WITH_CLOSER_FS'])
		self.propertyValWithCloserFS = float(row['PROPERTYVAL_WITH_CLOSER_FS']) if row['PROPERTYVAL_WITH_CLOSER_FS'] else 0.0

class FireStation:
	def __init__(self, id, name, fdid, station_num, pt):
		self.FSID = id
		self.name = name
		self.FDID = fdid
		self.station_num = station_num
		self.pt = pt

class ParcelPoint:
	__slots__ = ['NPARNO', 'PARVAL', 'FDID', 'pt', 'FSID_Nearest', 'FSID_NearestInDistrict', 'Dist_Nearest', 'Dist_NearestInDistrict']
	def __init__(self, l):
		self.NPARNO = l['NPARNO']
		self.PARVAL = float(l['PARVAL']) if l['PARVAL'] and (l['PARVAL'] != 'None') else 0.0
		self.FDID = l['FDID']
		self.pt = (float(l['lat']), float(l['lng']))
		self.FSID_Nearest = None
		self.FSID_NearestInDistrict = None
		self.Dist_Nearest = float('inf')
		self.Dist_NearestInDistrict = float('inf')
