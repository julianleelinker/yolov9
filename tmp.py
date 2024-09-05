final_classes = [
    'ANIMAL',
    'BARRICADE',
    'BICYCLE',
    'BUS',
    'BUS_STOP_SIGN',
    'CAR',
    'CLEAN_TRAFFIC_SIGN', # 'CLEAN_STOP_SIGN',
    'CONE',
    'DIRTY_TRAFFIC_SIGN', # 'DIRTY_STOP_SIGN', #
    'ETC',
    'HUMAN_LIKE',
    'JERSEY_BARRIER',
    'MOTORCYCLE',
    'NON_UPRIGHT',
    'PEDESTRIAN',
    'RIDER',
    'ROAD_CRACKS',
    'ROAD_PATCH',
    'ROAD_POTHOLES', #
    'TRAFFIC_LIGHT',
    'TRUCK',
    'UNCLEAR_ROAD_MARKING', #'UNCLEAR_LANE_MARKING', 'UNCLEAR_STOP_LINE'
    'WHEELCHAIR',
]


final_classes_map = {
    'ANIMAL':               'ANIMAL',
    'BARRICADE':            'BARRICADE',
    'BICYCLE':              'BICYCLE',
    'BUS':                  'BUS',
    'BUS_STOP_SIGN':        'BUS_STOP_SIGN',
    'CAR':                  'CAR',
    'CLEAN_STOP_SIGN':      'CLEAN_TRAFFIC_SIGN',
    'CLEAN_TRAFFIC_SIGN':   'CLEAN_TRAFFIC_SIGN',
    'CONE':                 'CONE',
    'DIRTY_STOP_SIGN':      'DIRTY_TRAFFIC_SIGN',
    'DIRTY_TRAFFIC_SIGN':   'DIRTY_TRAFFIC_SIGN',
    'ETC':                  'ETC',
    'HUMAN_LIKE':           'HUMAN_LIKE',
    'JERSEY_BARRIER':       'JERSEY_BARRIER',
    'MOTORCYCLE':           'MOTORCYCLE',
    'NON_UPRIGHT':          'NON_UPRIGHT',
    'PEDESTRIAN':           'PEDESTRIAN',
    'RIDER':                'RIDER',
    'ROAD_CRACKS':          'ROAD_CRACKS',
    'ROAD_PATCH':           'ROAD_PATCH',
    'ROAD_POTHOLES':        'ROAD_POTHOLES',
    'TRAFFIC_LIGHT':        'TRAFFIC_LIGHT',
    'TRUCK':                'TRUCK',
    'UNCLEAR_LANE_MARKING': 'UNCLEAR_ROAD_MARKING',
    'UNCLEAR_ROAD_MARKING': 'UNCLEAR_ROAD_MARKING',
    'UNCLEAR_STOP_LINE':    'UNCLEAR_ROAD_MARKING',
    'WHEELCHAIR':           'WHEELCHAIR',
}


final_classes = sorted(list(set(list(final_classes_map.values()))))
class_set = set(final_classes)
import ipdb; ipdb.set_trace()