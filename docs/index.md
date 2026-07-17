---
---

# Burke Fire Districts (vintage {{- site.data.fdenv.version -}})

## Online Maps

[Proximity Map][proxmap]: A proximity map showing color coded parcel centroids, with red indicating parcels whose
closest fire station is outside of its encompassing fire district.

## Summary

<style>
.dt td:nth-of-type(n+2) {text-align:center;}
</style>

{% include datatable.html data=site.data.burkefd %}

[proxmap]: proximitymap.html