import pathlib
import shutil


def create_relative_soft_link(actual_path):
    link_parent = pathlib.Path(actual_path.parent/str(actual_path.parent.name))
    link_parent.mkdir(exist_ok=True, parents=True)
    link_path = link_parent/actual_path.name

    if not pathlib.Path.exists(link_path):
        link_path.symlink_to(f'../{actual_path.name}')


def main():
    remove_old_links = False
    image_root = pathlib.Path('/home/julian/data/indus-innov/images/kaohsiung5gsmartcitydemo/')
    child_folders = [child for child in image_root.iterdir() if child.is_dir()]
    target_folders = [child/child.name for child in child_folders if (child/child.name).is_dir]
    assert(len(target_folders) == len(child_folders)), 'There are some folders that are not directories'

    if remove_old_links:
        remove_folders = [target/target.name for target in target_folders if (target/target.name).is_dir()]
        assert(len(target_folders) == len(remove_folders)), f'{remove_folders}'
        for remove_folder in remove_folders:
            print(f'removing {str(remove_folder)}')
            shutil.rmtree(remove_folder)

    for seq_root in target_folders:
        path_list = sorted(seq_root.glob('*.jpg'))
        print(f'{str(seq_root)}, num= {len(path_list)}')
        for path in path_list:
            create_relative_soft_link(path)


if __name__ == '__main__':
    main()