import os
import sys
import shutil
import checksumdir

#
# todo: check the hash of directory but it takes 10s ssd for all python
# hash = checksumdir.dirhash("c:\\temp")


def sync_pipeline_dirs(src_dir, dst_dir, ignore_names=[]):
    try:
        print("Begin sync")
        check_root_dirs_exist(src_dir, dst_dir)
        sync_dirs(src_dir, dst_dir, ignore_names)
        print("End sync with success")
    except Exception as e:
        print(e)
        print("End sync with failure!")




def check_root_dirs_exist(root_dir1, root_dir2) :
    if (not os.path.exists(root_dir1) and not os.path.isdir(root_dir1)) :
        raise Exception(root_dir1 + " doesn't exist")
    if (not os.path.exists(root_dir2) and not os.path.isdir(root_dir2)) :
        raise Exception(root_dir2 + " doesn't exist")


def remove_if_in_ignore_names(path, ignore_names):
    for n in ignore_names:
        if n in path:
            # print("ignoring this: {}".format(path))
            if os.path.exists(path):
                os.remove(path)
            return True

def sync_dirs(root_dir1, root_dir2, ignore_names=[]):
    for root1, dirs1, files1 in os.walk(root_dir1):
        # 1. first it creates directories
        for relative_path1 in dirs1 :
            full_path1 = os.path.join(root1, relative_path1)
            full_path2 = full_path1.replace(root_dir1, root_dir2)
            if os.path.exists(full_path2) and os.path.isdir(full_path2):
                continue
            if os.path.exists(full_path2) and os.path.isfile(full_path2):
                raise Exception("Cannot perform dir sync." + str(full_path2) + " should be a dir, not a file!")
            # Case 1 : dest dir does not exit
            if remove_if_in_ignore_names(full_path2, ignore_names):
                continue
            os.makedirs(full_path2)
            print("Directory " + str(full_path2) + " copied from " + str(full_path1))

        # 2. here it will create all files
        for file1 in files1:
            full_path1 = os.path.join(root1, file1)
            full_path2 = full_path1.replace(root_dir1, root_dir2)

            # Case 1 : the file does not exist in dest dir
            if (not os.path.exists(full_path2)) :
                if remove_if_in_ignore_names(full_path2, ignore_names):
                    continue
                shutil.copy2(full_path1, full_path2)
                print("File " + str(full_path2) + " copied from " + str(full_path1))
                continue

            # Case 2 : src file is more recent than dest file
            file1_last_modification_time = round(os.path.getmtime(full_path1))
            file2_last_modification_time = round(os.path.getmtime(full_path2))
            if (file1_last_modification_time > file2_last_modification_time):
                if remove_if_in_ignore_names(full_path2, ignore_names):
                    continue
                os.remove(full_path2)
                shutil.copy2(full_path1, full_path2)
                print("File " + str(full_path2) + " synchronized from " + str(full_path1))
                continue

def main():
    sync_pipeline_dirs(src_dir=sys.argv[1], dst_dir=sys.argv[2], ignore_names=["conda-meta"])


if __name__ == "__main__":
    main()
