# %%
import orjson
import pathlib
import tqdm
import pandas as pd
import numpy as np
import random
from collections import defaultdict
import copy
import argparse


unclear_levels = {'TWO_PERCENT', 'THREE_PERCENT', 'FOUR_PERCENT' }


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
    'PAVEMENT_DEFECT', # parent class

    # flurr incpmlete
    'LANE_MARKING', # flurr / incomplete
    'STOP_LINE', # flurr / incomplete
    'ROAD_MARKING', # flurr / incomplete

    # newly added for construction
    'CONE',
    'BARRICADE',
    'JERSEY_BARRIER',
}


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
    'BUS_STOP',
    'OBSTRUCTION',
    'SMOKE',
}


final_classes = [
    'ANIMAL',
    'BARRICADE', 
    'BICYCLE',
    'BUS',
    'BUS_STOP_SIGN',
    'CAR',
    'CLEAN_TRAFFIC_SIGN',
    'CONE',
    'ETC',
    'HUMAN_LIKE',
    'JERSEY_BARRIER',
    'MOTORCYCLE',
    'NON_UPRIGHT',
    'PEDESTRIAN',
    'POLE',
    'RIDER',
    'ROAD_CRACKS', #
    'ROAD_PATCH', #
    'ROAD_POTHOLES', #
    'STOP_SIGN',
    'TRAFFIC_LIGHT',
    'TRUCK',
    'UGLY_TRAFFIC_SIGN',
    'UNCLEAR_LANE_MARKING', #
    'UNCLEAR_ROAD_MARKING', #
    'UNCLEAR_STOP_LINE', #
    'WHEELCHAIR',
]

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


def get_timestamp_from_file_name(file_name):
    digitals = file_name.split('.')[0]
    if len(digitals) == 17 or len(digitals) == 20:
        digitals = digitals[1:]
    timestamp = int(digitals) 
    if len(digitals) == 16:
        timestamp *= 10**3
    return timestamp


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


def create_random_mask(num_images):
    pattern = [False]*10
    pattern[2:8] = [True]*6
    rand_ints = random.sample(range(num_images//len(pattern)), num_images//len(pattern)//5)
    val_mask = np.full(num_images, False, dtype=bool)
    train_mask = np.full(num_images, True, dtype=bool)
    for idx in rand_ints:
        val_mask[idx*len(pattern):(idx+1)*len(pattern)] = pattern
        train_mask[idx*len(pattern):(idx+1)*len(pattern)] = [False]*10
    return val_mask, train_mask


def find_good_split(focus_stats, target_ratio=0.12/0.8, tolerance=0.03):
    condition = False
    while not condition:
        val_mask, train_mask = create_random_mask(focus_stats.shape[0])
        ratio = np.divide(focus_stats[val_mask].sum(axis=0), focus_stats[train_mask].sum(axis=0))
        condition = np.logical_and(ratio < target_ratio+tolerance, ratio > target_ratio-tolerance).all()
        print(ratio, condition)
    return val_mask, train_mask


def main(args):
    file_path_root = '/home/julian/data/indus-innov/raw_anno'
    image_root     = '/home/julian/data/indus-innov/images/kaohsiung5gsmartcitydemo'
    bdd_anno_root  = '/home/julian/data/indus-innov/split-0327/bdd_anno'
    file_path_list = sorted(pathlib.Path(file_path_root).glob('*.json'))
    # file_path_list = file_path_list[7:8]


    # separate all data to different json that can be convert by bdd2coco, and check if there is any bad label
    not_supported_labels = []
    newly_added_categories = set()
    task_dict = {}
    df = pd.DataFrame(columns=(['timestamp', 'image_id', 'seq_id'] + final_classes))

    all_annos = {}
    for file_path in file_path_list:
        # create folder
        print(f'parsing {file_path}')
        with open(file_path, 'r') as f:
            data = orjson.loads(f.read())
        root_path = f'{bdd_anno_root}/{pathlib.Path(file_path).stem}'


        for key, value in tqdm.tqdm(data['jobBddData'].items()):
            assert key not in task_dict, f'{key} already exist'
            task_dict[key] = value
            # pathlib.Path(f'{root_path}/{key}').mkdir(exist_ok=True, parents=True)

            bdddata_id = 0 # 0 or 1?
            bdddata = value[bdddata_id]['bddData']

            all_annos[key] = {}
            for idx, frame in enumerate(bdddata['frame_list']):
                # frame info for splitting
                timestamp = get_timestamp_from_file_name(frame['name'])
                image_id = (df['timestamp'] == timestamp).sum()
                class_counter = {cat: 0 for cat in final_classes}
                all_annos[key][(timestamp, image_id)] = frame

                # create soft link
                create_soft_link(image_root, frame['lidarPlaneURLs'])

                for label in frame['labels']:

                    if (not label['category'] in interested_classes) and (not label['category'] in uninterested_classes):
                        newly_added_categories.add(label['category'])

                    if label['category'] in interested_classes:

                        # change category in place
                        if label['category'] in flurr_incomplete_classes:
                            if label['attributes']['INCOMPLETE'] in unclear_levels or label['attributes']['UNCLEAR'] in unclear_levels:
                                #label['category'] = 'UNCLEAR' # combine label
                                label['category'] = 'UNCLEAR_' + label['category'] # split label
                            else:
                                continue
                        # combine label
                        # if label['category'] in pavement_defect_candidate:
                        #     label['category'] = 'PAVEMENT_DEFECT'
                        # split label

                        if label['category'] == 'PAVEMENT_DEFECT':
                            label['category'] = label['attributes']['PAVEMENT_DEFECT']

                        if label['category'] in ['TRAFFIC_SIGN']:
                            if label['attributes']['DIRTY'] == 'YES':
                                label['category'] = 'DIRTY_' + label['category']
                            else:
                                label['category'] = 'CLEAN_' + label['category']


                        class_counter[label['category']] += 1
                        # get box2d
                        if 'box2d' in label or 'poly2d' in label:
                            # can be handled by bdd2coco/bdd2yolo later
                            pass 
                        elif 'segment' in label:
                            bbox = label['segment']['bbox']
                            label['box2d'] = {
                                'x1': bbox[0],
                                'y1': bbox[1],
                                'x2': bbox[0]+bbox[2],
                                'y2': bbox[1]+bbox[3],
                            }
                            label.pop('segment')
                        else:
                            print('not suppported shape')
                            print(label)
                            not_supported_labels.append(label)

                pddata = pd.DataFrame(dict(timestamp=timestamp, image_id=image_id, seq_id=0, **class_counter), index=[0])
                df = pd.concat([df, pddata], ignore_index=True)

            # save processed bdd to json file
            # if not args.dry:
            #     json_path = f'{root_path}/{key}/{bdddata_id}.json'
            #     with open(json_path, 'w') as f:
            #         f.write(orjson.dumps(bdddata).decode())


    df = df.sort_values(by=['image_id', 'timestamp'], ascending=True)
    sequence_time_diff = 5*10**8 # 0.5 sec
    cur_seq_id = 0
    last_timestamp = df.iloc[0]['timestamp']
    df['seq_id'] = cur_seq_id
    for idx, row in df.iterrows():
        if row['timestamp'] - last_timestamp > sequence_time_diff:
            cur_seq_id += 1
        df.at[idx, 'seq_id'] = cur_seq_id
        last_timestamp = row['timestamp']
    print(df.sum())
    stats_array = df[final_classes].to_numpy(dtype=int)
    focus_stats = stats_array[:, [16,17,18,23,24,25]]
    target_ratio, tolerance = 0.12/0.8, 0.05
    val_mask, train_mask = find_good_split(focus_stats, target_ratio=target_ratio, tolerance=tolerance)
    print(f'newly added labels: {newly_added_categories}')
    print(f'not_supported_labels: {len(not_supported_labels)}')
    print(f'done spliting with target_ratio {target_ratio} and tolerance {tolerance}')

    # save split id
    for key, frame_list in tqdm.tqdm(all_annos.items()):
        bdddata_train = copy.deepcopy(bdddata)
        bdddata_val = copy.deepcopy(bdddata)
        bdddata_train['frame_list'] = []
        bdddata_val['frame_list'] = []
        pathlib.Path(f'{bdd_anno_root}/train/{key}').mkdir(exist_ok=True, parents=True)
        pathlib.Path(f'{bdd_anno_root}/val/{key}').mkdir(exist_ok=True, parents=True)
        for (timestamp, image_id) in frame_list:
            # check train or val
            index = df.index[(df['timestamp'] == timestamp) & (df['image_id'] == image_id)].tolist()
            index = df.index.get_loc(index[0])
            if train_mask[index]:
                bdddata_train['frame_list'].append(frame_list[(timestamp, image_id)])
            elif val_mask[index]:
                bdddata_val['frame_list'].append(frame_list[(timestamp, image_id)])

        json_path = f'{bdd_anno_root}/train/{key}/{bdddata_id}.json'
        with open(json_path, 'w') as f:
            f.write(orjson.dumps(bdddata_train).decode())

        json_path = f'{bdd_anno_root}/val/{key}/{bdddata_id}.json'
        with open(json_path, 'w') as f:
            f.write(orjson.dumps(bdddata_val).decode())
    print(f'bdd anno parse to {bdd_anno_root} done!')
    import ipdb; ipdb.set_trace()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    # parser.add_argument('--weights', type=str, help='weights path')
    parser.add_argument('--dry', action='store_true', help='dry run')
    args = parser.parse_args()
    main(args)