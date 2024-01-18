from typing import List, Any
from enum import Enum
import operator


is_logging = False


def log(obj: Any) -> None:
    if is_logging:
        print(obj)


class MapType(Enum):
    seed_to_soil = 1,
    soil_to_fertilizer = 2
    fertilizer_to_water = 3
    water_to_light = 4
    light_to_temperature = 5
    temperature_to_humidity = 6
    humidity_to_location = 7


class SourceToDestinationMap:
    def __init__(self, map_data: str):
        map_parts = map_data.strip().split()
        self.destination = int(map_parts[0])
        self.source = int(map_parts[1])
        self.range_length = int(map_parts[2])


class SourceMappers:
    def __init__(self):
        self.seeds: List[int] = []
        self.seed_to_soil: List[SourceToDestinationMap] = []
        self.soil_to_fertilizer: List[SourceToDestinationMap] = []
        self.fertilizer_to_water: List[SourceToDestinationMap] = []
        self.water_to_light: List[SourceToDestinationMap] = []
        self.light_to_temperature: List[SourceToDestinationMap] = []
        self.temperature_to_humidity: List[SourceToDestinationMap] = []
        self.humidity_to_location: List[SourceToDestinationMap] = []

    def set_seeds(self, seed_data: str):
        seeds = seed_data.partition(":")
        for seed in seeds[2].strip().split():
            self.seeds.append(int(seed))

    def get_map_for_type(self, map_type: MapType) -> List[SourceToDestinationMap]:
        match map_type:
            case MapType.seed_to_soil:
                return self.seed_to_soil
            case MapType.soil_to_fertilizer:
                return self.soil_to_fertilizer
            case MapType.fertilizer_to_water:
                return self.fertilizer_to_water
            case MapType.water_to_light:
                return self.water_to_light
            case MapType.light_to_temperature:
                return self.light_to_temperature
            case MapType.temperature_to_humidity:
                return self.temperature_to_humidity
            case MapType.humidity_to_location:
                return self.humidity_to_location

    def append(self, map_data: str, map_type: MapType):
        map_to_modify = self.get_map_for_type(map_type)
        map_to_modify.append(SourceToDestinationMap(map_data))

    def sort_maps(self):
        self.seed_to_soil.sort(key=operator.attrgetter('source'))
        self.soil_to_fertilizer.sort(key=operator.attrgetter('source'))
        self.fertilizer_to_water.sort(key=operator.attrgetter('source'))
        self.water_to_light.sort(key=operator.attrgetter('source'))
        self.light_to_temperature.sort(key=operator.attrgetter('source'))
        self.temperature_to_humidity.sort(key=operator.attrgetter('source'))
        self.humidity_to_location.sort(key=operator.attrgetter('source'))

    def get_location_for_seed(self, seed: int) -> int:
        log(f"Getting location for seed {seed}")
        seed_map = f"{seed}->"
        dest = self.get_dest_for_source(seed, MapType.seed_to_soil)
        seed_map += f"{dest}->"
        dest = self.get_dest_for_source(dest, MapType.soil_to_fertilizer)
        seed_map += f"{dest}->"
        dest = self.get_dest_for_source(dest, MapType.fertilizer_to_water)
        seed_map += f"{dest}->"
        dest = self.get_dest_for_source(dest, MapType.water_to_light)
        seed_map += f"{dest}->"
        dest = self.get_dest_for_source(dest, MapType.light_to_temperature)
        seed_map += f"{dest}->"
        dest = self.get_dest_for_source(dest, MapType.temperature_to_humidity)
        seed_map += f"{dest}->"
        dest = self.get_dest_for_source(dest, MapType.humidity_to_location)
        seed_map += f"{dest}"
        log(seed_map)
        return dest

    def get_dest_for_source(self, source: int, map_type: MapType) -> int:
        the_map = self.get_map_for_type(map_type)

        # quick escape if outside range of map
        if source < the_map[0].source or source > the_map[-1].source + the_map[-1].range_length:
            return source

        for idx in range(len(the_map)):
            current_map = the_map[idx]

            # source is less than the current map start
            if source < current_map.source:
                return source

            if current_map.source <= source <= current_map.source + current_map.range_length - 1:
                offset = source - current_map.source
                return current_map.destination + offset

        return source


source_mappers = SourceMappers()
current_map_type = MapType.seed_to_soil

file_name = "input_small"

with open(file_name, encoding="utf-8") as f:
    for line in f:
        if line.startswith("seeds:"):
            source_mappers.set_seeds(line)
            continue

        if line.strip().isspace() or line.strip() == "":
            continue

        if line.startswith("seed-to-soil"):
            current_map_type = MapType.seed_to_soil
            continue

        if line.startswith("soil-to-fertilizer"):
            current_map_type = MapType.soil_to_fertilizer
            continue

        if line.startswith("fertilizer-to-water"):
            current_map_type = MapType.fertilizer_to_water
            continue

        if line.startswith("water-to-light"):
            current_map_type = MapType.water_to_light
            continue

        if line.startswith("light-to-temperature"):
            current_map_type = MapType.light_to_temperature
            continue

        if line.startswith("temperature-to-humidity"):
            current_map_type = MapType.temperature_to_humidity
            continue

        if line.startswith("humidity-to-location"):
            current_map_type = MapType.humidity_to_location
            continue

        source_mappers.append(line, current_map_type)

source_mappers.sort_maps()

seed_locations: List[int] = []
for s in source_mappers.seeds:
    location = source_mappers.get_location_for_seed(s)
    seed_locations.append(location)

seed_locations.sort()
log(seed_locations)
print(f"Part 1: {seed_locations[0]}")


# This works for small input but chokes on larger input because it's essentially brute-forcing a solution
# and there are millions of seeds to consider. It would conceivably run given enough CPU time however there are
# far more elegant and efficient solutions using interval mapping (see learning.py for one approach)
minimum_seed_number = source_mappers.seeds[0]
minimum_location_number = source_mappers.get_location_for_seed(minimum_seed_number)

for index in range(int(len(source_mappers.seeds)/2)):
    seed_number = source_mappers.seeds[index*2]
    seed_range = source_mappers.seeds[index*2 + 1]

    current_seed_number = seed_number
    current_location_number = source_mappers.get_location_for_seed(current_seed_number)

    if current_location_number < minimum_location_number:
        minimum_seed_number = current_seed_number
        minimum_location_number = current_location_number

    current_seed_number = seed_number + seed_range - 1
    current_location_number = source_mappers.get_location_for_seed(current_seed_number)

    for seed_offset in range(seed_range):
        current_seed_number = seed_number + seed_offset
        current_location_number = source_mappers.get_location_for_seed(current_seed_number)

        if current_location_number < minimum_location_number:
            minimum_seed_number = current_seed_number
            minimum_location_number = current_location_number

log(f"{minimum_seed_number=}")
print(f"Part 2: {minimum_location_number}")
