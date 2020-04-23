import os
import numpy as np
import json
import cv2
import shutil


SLIGHT_DEFECT = ['hengdaomao2', 'lamao2']
DEFECT = ['hengdaomao1', 'hengdaomao2', 'hengdaomao3', 'lamao1', 'lamao2', 'yamao', 'zangwu', 'yousha', 'kongxinmao',
          'gerong', 'chaoduan']

image_width = 300
image_height = 400
x_stride = 100
y_stride = 100


def slide_window_split(input_path, output_path):
    """从json标注文件中读取图片的标注信息，并利用相应的判别矩阵分类"""
    input_path_list = os.listdir(input_path)
    json_list = [item for item in input_path_list if 'json' in item]
    for json_item in json_list:
        # 读取每个json文件的数据
        # if json_item != '-1260943830673120540.json':  # 测试no_defect的图片分割是否正确
        #     continue
        print('splitting {}'.format(json_item))
        image_name = json_item.split('.')[0] + '.BMP'
        with open(input_path + json_item, 'r') as f:
            json_data = json.load(f)
        image_data = cv2.imread(input_path + image_name)
        # 调试输出图片的维度信息
        # print(image_data.shape)
        # 对每张图片生成对应的瑕疵判别矩阵
        defect_mask_list = [np.zeros_like(image_data) for _ in range(len(DEFECT))]
        # 调试输出判断矩阵的维度信息
        # print(defect_mask_list[0].shape)
        # 对每张图片的瑕疵区域用灰度图填充，生成判别矩阵,对轻微的瑕疵填充1，其他瑕疵填充2，因为每一张图片可能有多种瑕疵，所以用for
        for shape in json_data['shapes']:
            defect_name = shape['label']
            if defect_name == 'no':
                print('no defect in {}'.format(json_data['imagePath']))
                continue
            point_list = shape['points']
            point_array = np.array([point_list], np.int32)
            if defect_name in SLIGHT_DEFECT:
                index = DEFECT.index(defect_name)
                cv2.fillPoly(defect_mask_list[index], point_array, (1, 1, 1))
            else:
                index = DEFECT.index(defect_name)
                cv2.fillPoly(defect_mask_list[index], point_array, (2, 2, 2))
            # 调试显示灰度矩阵
            # cv2.imshow(defect_name, defect_mask_list[index])
            # cv2.waitKey(0)
        # 寻找defect_mask_list中瑕疵最严重的那种瑕疵作为该图像的瑕疵种类，为defect_name_max
        if defect_name != 'no':
            defect_name_max = defect_name
            defect_mask_max = defect_mask_list[index].sum()
            for i, defect_mask in enumerate(defect_mask_list):
                defect_mask_sum = defect_mask.sum()
                if defect_mask_sum > defect_mask_max:
                    defect_name_max = DEFECT[i]
        # 滑动窗口分割图片
        for x in range(10):
            # for x in range(1):
            for y in range(13):
                # for y in range(1):
                x_min = x * x_stride
                x_max = image_width + x * x_stride
                y_min = y * y_stride
                y_max = image_height + y * y_stride
                image_item = image_data[x_min:x_max, y_min:y_max, :]
                if defect_name != 'no':
                    defect_mask_item = defect_mask_list[DEFECT.index(defect_name_max)][x_min:x_max, y_min:y_max, :]
                    is_defect = defect_mask_item.sum()
                    if is_defect > 0:
                        image_item_label = defect_name_max
                    else:
                        image_item_label = 'no_defect'
                else:
                    image_item_label = 'no_defect'
                file_base_name = json_item.split('.')[0]
                file_name = '{}_{}_{}'.format(file_base_name, x, y)
                defect_name_max_path = image_item_label + '/'
                path_name = output_path + defect_name_max_path
                if not os.path.exists(path_name):
                    os.makedirs(path_name)
                path_file_name = path_name + file_name + '.jpg'
                cv2.imwrite(path_file_name, image_item)


def test():
    my_list = [1, 2, 3]
    for item in my_list:
        index = my_list.index(item)
        print('{}'.format(index))


def list_split_number(images_path):
    path_name_list = os.listdir(images_path)
    length_list = {}
    for path_name_item in path_name_list:
        path_file_name = os.path.join(images_path, path_name_item)
        path_file_name_list = os.listdir(path_file_name)
        length_item = len(path_file_name_list)
        length_list.append(length_item)
        print('{} : {} 张'.format(path_name_item, length_item))
    print('共有：{} 张'.format(sum(length_list)))


def list_origin_number(input_path):
    input_path_list = os.listdir(input_path)
    origin_number = len(input_path_list) / 2
    return origin_number


def move_origin_images(input_path, output_path1, output_path2):
    origin_images_list = os.listdir(input_path)
    if not os.path.exists(output_path1):
        os.makedirs(output_path1)
    if not os.path.exists(output_path2):
        os.makedirs(output_path2)
    for i, item in enumerate(origin_images_list):
        origin_file_path = input_path + item
        if i <= 1223:
            destination_file_path1 = output_path1 + item
            shutil.move(origin_file_path, destination_file_path1)
        else:
            destination_file_path2 = output_path2 + item
            shutil.move(origin_file_path, destination_file_path2)


def list_origin_images(input_path):
    input_path_list = os.listdir(input_path)
    length = len(input_path_list)
    print('origin images : {}'.format(length))


def move_to_disk(input_path, output_path):
    origin_path_list = {}
    input_path_list = os.listdir(input_path)
    for input_path_item in input_path_list:
        defect_path_item = input_path + input_path_item + '/'
        origin_path_list.append(defect_path_item)
    for origin_path_item in origin_path_list:
        origin_file_path_item = os.listdir(origin_path_item)
        for file_item in origin_file_path_item:
            shutil.move()


if __name__ == '__main__':
    # 分割图片
    inputs_path = './images1/'
    outputs_path = './split_images/'
    slide_window_split(inputs_path, outputs_path)

    inputs_path = './images2/'
    outputs_path = './split_images/'
    slide_window_split(inputs_path, outputs_path)

    # 原始图片个数
    # print('origin number:{}'.format(list_origin_number('./images/')))

    # 将原始图像移动到两个文件夹，方便后续处理
    # move_origin_images('./images/', './images1/', './images2/')

    # 输出分割后各类别有多少张图像，以及总共的图像数量
    # path = './split_images/'
    # split_sum = list_split_number(path)

    # 输出移动到两个文件夹后的图像个数
    # list_origin_images('./images1/')
    # list_origin_images('./images2/')
