from django.contrib.gis.geos import GEOSGeometry, MultiPolygon, Polygon, GeometryCollection
from json import loads as load_json
from json import dumps as dump_json

def geojson_to_polygons(json, original_project, desired_projection):
    """Returns generator of GEOSGeometry polygons"""
    def to_geos(json_dict_polygon):
        """Return GEOSGeometry polygon from polygon dictionary"""
        json_dict_polygon = json_dict_polygon['geometry']
        geo = GEOSGeometry(dump_json(json_dict_polygon))
        geo.srid = original_project
        # geo.set_srid(original_project) # Fix manual selection tools bug (20/01/2013)
        geo.transform(desired_projection)
        return geo
    if json == '':
        raise ValueError('Json string is empty')
    
    try:
        json_dict = load_json(json)
    except ValueError:
        raise ValueError('Incorrect json format')
    
    json_type = json_dict.get('type', 'fail')
    
    if json_type == 'Feature':
        json_dict_polygons = json_dict
    elif json_type == 'FeatureCollection': 
        json_dict_polygons = json_dict.get('features')
    else:
        raise Exception('Incorrect json format')
        
    return (to_geos(poly) for poly in json_dict_polygons)
    
def polygons_to_mpoly(polygons):
    # This includes both polygons and multipolygons
    polygons = [poly for poly in polygons]
    return GeometryCollection(*polygons)

def shapefile_to_geojson(shape_layer):
    geoms = shape_layer.get_geoms()
    for geom in geoms:
        geom.transform(3857)
    # Create required enteries for GeoJSON representation
    geo_json = {"type": "FeatureCollection",
               "features": [
                   {"type": "Feature",
                    "geometry": load_json(geom.geojson),
                    "properties":{}
                    }
               for geom in geoms]}
    return dump_json(geo_json)

def is_polygon(layer):
    if str(layer.geom_type) == 'Polygon':
        return True
    else:
        return False
def as_json(message):
    return dump_json(message)
