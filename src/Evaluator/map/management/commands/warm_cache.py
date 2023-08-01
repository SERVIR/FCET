from django.core.management.base import BaseCommand, CommandError
import regions.services as region_services
import map.services as map_services

class Command(BaseCommand):
    help = 'Cache long running queries to make the tool usable'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # Cache Policy Areas

        #Add function to clear the cache
        self.stdout.write("Caching policy areas")
        policy_areas = region_services.get_policy_areas()
        policy_areas = [area['name'] for area in policy_areas]
        num_policies = len(policy_areas)
        counter = 0.0
        for area in policy_areas:
            map_services.clear_cache_points_by_policy(area)
            map_services.get_points_by_policy(area)
            counter += 1.0
            progress = (counter/num_policies)*100
            self.stdout.write("progress: {}%".format(progress))

        # Cache Study Regions
        self.stdout.write("Caching study areas")
        regions = region_services.get_regions()
        num_regions = len(regions)
        counter = 0.0
        for region in regions:
             map_services.clear_cache_points_by_region(str(region))
             map_services.get_points_by_region(str(region))
             counter += 1.0
             progress = (counter/num_regions)*100
             self.stdout.write("progress: {}%".format(progress))
