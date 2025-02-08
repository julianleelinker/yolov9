
import pathlib
import shutil
import tqdm

root_dir = '/home/julian/data/indus-innov/mobility-YOLO-old'
target_dir = '/home/julian/data/indus-innov/mobility-YOLO'

# img_list = sorted(pathlib.Path(root_dir).rglob('*.jpg'))
# for img_path in tqdm.tqdm(img_list):
#     new_dir = f"{target_dir}/{str(img_path).split('/')[-7]}/{str(img_path).split('/')[-6]}/{str(img_path).split('/')[-4]}"
#     pathlib.Path(new_dir).mkdir(parents=True, exist_ok=True)
#     src_file = img_path.resolve()
#     dst_file = pathlib.Path(new_dir)/src_file.name
#     print(f'{src_file} to {dst_file}')
#     # copy src_file to new_dir using shutil
#     shutil.copy(src_file, dst_file)

label_list = sorted(pathlib.Path(root_dir).rglob('*.txt'))

for label_path in tqdm.tqdm(label_list):
    new_dir = f"{target_dir}/{str(label_path).split('/')[-7]}/{str(label_path).split('/')[-6]}/{str(label_path).split('/')[-4]}"
    pathlib.Path(new_dir).mkdir(parents=True, exist_ok=True)
    src_file = label_path.resolve()
    dst_file = pathlib.Path(new_dir)/src_file.name
    print(f'{src_file} to {dst_file}')
    # copy src_file to new_dir using shutil
    shutil.copy(src_file, dst_file)