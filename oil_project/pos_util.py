from pyproj import Transformer

def wgs84_to_katec(lat, lon):
    # WGS84(EPSG:4326) -> KATEC 변환 
    proj_katec = (
        "+proj=tmerc +lat_0=38 +lon_0=128 +k=0.9999 +x_0=400000 +y_0=600000 "
        "+ellps=bessel +towgs84=-145.907,505.034,685.756,-1.162,2.347,1.592,6.342 +units=m +no_defs"
    )
    
    transformer = Transformer.from_crs("epsg:4326", proj_katec, always_xy=True)    
    katec_x, katec_y = transformer.transform(lon, lat)
    
    return katec_x, katec_y

def katec_to_wgs84(x, y):
    # KATEC -> WGS84
    proj_katec = (
        "+proj=tmerc +lat_0=38 +lon_0=128 +k=0.9999 +x_0=400000 +y_0=600000 "
        "+ellps=bessel +towgs84=-145.907,505.034,685.756,-1.162,2.347,1.592,6.342 +units=m +no_defs"
    )
    
    transformer = Transformer.from_crs(proj_katec, "epsg:4326", always_xy=True)    
    lon, lat = transformer.transform(x, y)

    return lat, lon