# %%
import orjson
import pathlib
import tqdm

od_classes = {
    # box2d classes
    'CAR',
    'TRUCK',
    'BUS',
    'MOTORCYCLE',
    'BICYCLE',
    'WHEELCHAIR',
    'ETC', #
    'PEDESTRIAN',
    'NON_UPRIGHT', #
    'HUMAN_LIKE', #
    'RIDER',
    'ANIMAL',
    'POLE', # not used
    'TRAFFIC_SIGN',
    'TRAFFIC_LIGHT',
    'BUS_STOP_SIGN',
    'STOP_SIGN',
    'PAVEMENT_DEFECT',
    'UNCLEAR',
}

interested_classes = {
    # box2d classes
    'CAR',
    'TRUCK',
    'BUS',
    'MOTORCYCLE',
    'BICYCLE',
    'WHEELCHAIR',
    'ETC', #
    'PEDESTRIAN',
    'NON_UPRIGHT', #
    'HUMAN_LIKE', #
    'RIDER',
    'ANIMAL',
    'POLE', # not used
    'TRAFFIC_SIGN',
    'TRAFFIC_LIGHT',
    'BUS_STOP_SIGN',
    'STOP_SIGN',

    # segment or poly2d classes
    'ROAD_CRACKS', # newly added
    'ROAD_PATCH', # newly added
    'ROAD_POTHOLES', # newly added
    'PAVEMENT_DEFECT',

    # flurr incpmlete
    'LANE_MARKING', # flurr / incomplete
    'STOP_LINE', # flurr / incomplete
    'ROAD_MARKING', # flurr / incomplete

    # newly added for construction
    'CONE',
    'BARRICADE',
    'JERSEY_BARRIER',
}

unclear_levels = {'TWO_PERCENT', 'THREE_PERCENT', 'FOUR_PERCENT' }


interested_to_seg_classes = {
    # below threee detect as same class
    'ROAD_CRACKS', # newly added
    'ROAD_PATCH', # newly added
    'ROAD_POTHOLES', # newly added
    'PAVEMENT_DEFECT',

    'LANE_MARKING', # flurr / incomplete
    'STOP_LINE', # flurr / incomplete
    'ROAD_MARKING', # flurr / incomplete

    # newly added for construction
    'CONE',
}
    
pavement_defect_candidate = {
    'PAVEMENT_DEFECT', # parent class
    'ROAD_CRACKS', # newly added
    'ROAD_PATCH', # newly added
    'ROAD_POTHOLES', # newly added
}

uninterested_classes = {
    # below four detect as same class 
    'PAINTED_ISLAND', # flurr / incomplete???
    'MOTORCYCLE_WAITING_ZONE',
    'ROAD',
    'SIDEWALK',
    # 'ROAD_DAMAGE', # not used
    'CONE',
    'BARRICADE',
    'JERSEY_BARRIER',
    'BUS_STOP',
    'OBSTRUCTION',
    'SMOKE',
}

flurr_incomplete_classes = {
    'LANE_MARKING', # flurr / incomplete
    'STOP_LINE', # flurr / incomplete
    # 'PAINTED_ISLAND', # flurr / incomplete 
    'ROAD_MARKING', # flurr / incomplete
}

od_mislabeled_as_seg_uuid_list = {
    'f9deb57e-9fbe-4457-b84e-0d5c4bebce29',
    'd748094a-7389-46b7-841c-f0b39d180fda',
}

def get_image_from_lidar_plane_url(image_root, lidar_plane_url, repeat):
    parent_name = '/' + lidar_plane_url[0].split('/')[0]
    file_name = '/' + lidar_plane_url[0].split('/')[1]
    actual_path = image_root + parent_name*repeat + file_name
    return pathlib.Path(actual_path)


def create_soft_link(image_root, lidar_plane_url):
    assert len(lidar_plane_url) == 1
    actual_path = get_image_from_lidar_plane_url(image_root, lidar_plane_url, repeat=2)
    assert pathlib.Path.exists(actual_path), f'{actual_path} not exist'
    link_path = get_image_from_lidar_plane_url(image_root, lidar_plane_url, repeat=3)
    link_path.parent.mkdir(exist_ok=True, parents=True)
    if not pathlib.Path.exists(link_path):
        link_path.symlink_to(actual_path)
        print(f'create soft link: link {link_path} -> source {actual_path}')


# %%
# file_path_list = [
#     '/home/julian/data/indus-innov/TIIP-S1-1000.json',
#     '/home/julian/data/indus-innov/TIIP-S2-1000.json',
# ]

# file_path_list = [
#     '/home/julian/data/indus-innov/65543e93266c1b7a5656bfb6-0-pipelineBDDPlusSet.json',
#     '/home/julian/data/indus-innov/65543ecb266c1b7a5656cc86-0-pipelineBDDPlusSet.json',
# ]

file_path_root = '/home/julian/data/indus-innov/raw_anno'
image_root     = '/home/julian/data/indus-innov/images/kaohsiung5gsmartcitydemo'
bdd_anno_root  = '/home/julian/data/indus-innov/0311/bdd_anno'
file_path_list = sorted(pathlib.Path(file_path_root).glob('*.json'))


# %% select one for inspecting data
# file_path = file_path_list[0]
# with open(file_path, 'r') as f:
#     data = orjson.loads(f.read())
# access one example frame
# ex_frame_list = data['jobBddData']['65543f76266c1b7a5656dadd'][0]['bddData']['frame_list']


# %% separate all data to different json that can be convert by bdd2coco, and check if there is any bad label
flurr_incomplete_labels = []
bad_labels = []
not_supported_labels = []
newly_added_categories = set()
labeled_images = set()

counter = {
    'CONE': 0,
    'BARRICADE': 0,
    'JERSEY_BARRIER': 0,
}

for file_path in file_path_list:
    print(f'parsing {file_path}')
    with open(file_path, 'r') as f:
        data = orjson.loads(f.read())
    root_path = f'{bdd_anno_root}/{pathlib.Path(file_path).stem}'
    pathlib.Path(root_path).mkdir(exist_ok=True, parents=True)


    for key, val in tqdm.tqdm(data['jobBddData'].items()):
        pathlib.Path(f'{root_path}/{key}').mkdir(exist_ok=True, parents=True)

        # json1 = val[0]
        # json2 = val[1]
        # result = deepdiff.DeepDiff(json1, json2)
        # for key in result['values_changed'].keys():
        #     assert key in accept_changes, f'{key} not in accept_changes'

        i = 0
        bdddata = val[0]['bddData']
        unlabelled_frames = []
        for frame_id, frame in enumerate(bdddata['frame_list']):

            if len(frame['labels']) != 0:
                # print('no label')
                create_soft_link(image_root, frame['lidarPlaneURLs'])
            else:
                unlabelled_frames.append(frame_id)

            for label in frame['labels']:

                if (not label['category'] in interested_classes) and (not label['category'] in uninterested_classes):
                    newly_added_categories.add(label['category'])

                if label['category'] in interested_classes:
                    if 'box2d' in label:
                        continue
                    if label['category'] in interested_to_seg_classes or label['uuid'] in od_mislabeled_as_seg_uuid_list:

                        if label['category'] in flurr_incomplete_classes:
                            if label['attributes']['INCOMPLETE'] in unclear_levels or label['attributes']['UNCLEAR'] in unclear_levels:
                                #label['category'] = 'UNCLEAR' # combine label
                                label['category'] = 'UNCLEAR_' + label['category'] # split label
                            else:
                                break

                        # combine label
                        # if label['category'] in pavement_defect_candidate:
                        #     label['category'] = 'PAVEMENT_DEFECT'

                        # split label
                        if label['category'] == 'PAVEMENT_DEFECT':
                            label['category'] = label['attributes']['PAVEMENT_DEFECT']

                        if 'segment' in label:
                            bbox = label['segment']['bbox']
                            label['box2d'] = {
                                'x1': bbox[0],
                                'y1': bbox[1],
                                'x2': bbox[0]+bbox[2],
                                'y2': bbox[1]+bbox[3],
                            }
                            # label['box2d'] = {
                            #     'x1': 100,
                            #     'y1': 300,
                            #     'x2': 200,
                            #     'y2': 400,
                            # }
                            label.pop('segment')
                        elif 'poly2d' in label:
                            pass
                            # ex_label = label
                            # vertices = label['poly2d'][0]['vertices']
                            # xs = [xy[0] for xy in vertices]
                            # ys = [xy[1] for xy in vertices]
                            # label['box2d'] = {
                            #     'x1': min(xs)+1,
                            #     'y1': min(ys)+1,
                            #     'x2': max(xs)-1,
                            #     'y2': max(ys)-1,
                            # }
                            # label.pop('poly2d')
                        # else:
                        #     print('not suppported shape')
                        #     print(label)
                        #     not_supported_labels.append(label)
                        # assert label['box2d']['x1'] > 0
                        # assert label['box2d']['x2'] < 1920
                        # assert label['box2d']['y1'] > 0
                        # assert label['box2d']['y2'] < 1280

                        #     }
                    else:
                        bad_labels.append(label)
        for frame_id in unlabelled_frames[::-1]:
            bdddata['frame_list'].pop(frame_id)

        # save tmp to json file
        json_path = f'{root_path}/{key}/{i}.json'
        with open(json_path, 'w') as f:
            f.write(orjson.dumps(bdddata).decode())


print(f'newly added labels: {newly_added_categories}')
print(f'not_supported_labels: {len(not_supported_labels)}')
print(f'bad_labels: {len(bad_labels)}')
print(f'bdd anno parse to {bdd_anno_root} done!')

