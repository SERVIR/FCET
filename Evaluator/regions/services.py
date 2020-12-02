from .models import Region, PolicyArea
from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
import os


def get_region_polygon(fid):
    """
    returns the polygon of a specific region

    :param request: django request parameter
    :param region: id of region
    :return: geodjango/geos multipolygon
    """
    return Region.objects.get(id=fid).poly


def get_regions():
    return list(Region.objects.all().values_list('id', flat=True))


def get_region_country(fid):
    return Region.objects.get(id=fid).country


def get_policy_areas():
    """
    retrieve names of all available policy areas and related ids
    """
    #cast to list is needed since django does not actually return a list
    return list(PolicyArea.objects.all().distinct('name').values('name'))


def get_policy_area_polygons(policy_names):
    """
    retrieve policy area polygon to be used for querying individual data points for treatment selection

    :param fid: id of policy area that we would like to return
    :return: MultiPolygon object
    """
    policy = PolicyArea.objects.filter(name=policy_names).all()
    policy_polygons = [polygon.poly for polygon in policy]
    return policy_polygons


def _load_policy_area_shapefile(shapefile_name, policy_area_name):
    """
    Load in shapefile to add a policy area to the app to be used for treatment selection

    :param shapefile_name: The name or directory of the target shapefile located in region/data/policy_areas
    :param policy_area_name: A descriptive front-end friendly name.
    :return:
    """
    # Remove this temporary measure for manual testing
    # PolicyArea.objects.all().delete()

    # Load in layer from shapefile
    data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data', 'policy_areas', shapefile_name)) # check that this leads to the correct path
    ds = DataSource(data_path)
    layer = ds[0]

    # Convert shapefile features into django models accounting for polygon vs multipolygon
    policy_features = []
    for feature in layer:
        feature = GEOSGeometry(feature.geom.wkt)
        if feature.geom_type == 'Polygon':
            feature = MultiPolygon(feature)

        policy_features.append(PolicyArea(poly=feature, name=policy_area_name, shapefile_name=shapefile_name))

    # Add models to database using bulk for efficiency
    PolicyArea.objects.bulk_create(policy_features)


