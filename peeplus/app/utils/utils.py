# 改写文本文件
def replace_str(ori_path, old_str, new_str, tar_path = None):
    file_data = ""
    with open(ori_path, "r", encoding="utf-8") as f:
        for line in f:
            if old_str in line:
                line = line.replace(old_str, new_str)
            file_data += line

    if tar_path is not None:
        with open(tar_path, "w", encoding="utf-8") as f:
            f.write(file_data)
    with open(ori_path, "w", encoding="utf-8") as f:
        f.write(file_data)
