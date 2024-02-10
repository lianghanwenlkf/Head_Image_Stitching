# -*- coding: utf-8 -*-
import math
import os
import csv
import yaml
import logging
import requests
import pandas as pd
from PIL import Image
from tqdm import tqdm
from time import sleep
from datetime import datetime


def create_folder(folder_path):
    # 检查文件夹是否存在
    if not os.path.exists(folder_path):
        # 如果不存在，则创建文件夹
        os.makedirs(folder_path)
        print(f"文件夹创建成功: {folder_path}")
    else:
        print(f"文件夹已存在: {folder_path}")


def download_qq_head_img(qq_path, head_img_path):
    with open(qq_path, 'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        print('download_qq_head_img')
        sleep(0.1)
        for i, row in tqdm(enumerate(csv_reader)):
            if i > 0:
                name = row[0]
                url = f'https://q1.qlogo.cn/g?b=qq&nk={row[2][:-7]}&s=640'
                try:
                    response = requests.get(url)

                    # 如果请求成功 (状态码为200)
                    if response.status_code == 200:
                        # 以二进制模式写入文件
                        head_img_file_path = head_img_path + '/qq_' + name + '.jpg'
                        with open(head_img_file_path, 'wb') as file:
                            file.write(response.content)
                    else:
                        print(f"文件下载失败, 状态码: {response.status_code}")

                except Exception as e:
                    print(f"发生错误: {e}")


def download_wechat_head_img(wechat_path, head_img_path):
    excel_file = pd.read_excel(wechat_path)
    print('download_wechat_head_img')
    sleep(0.1)
    for index, row in tqdm(excel_file.iterrows()):
        if pd.notna(row['Remark']):
            name = row['Remark']
        else:
            name = row['NickName']
        url = row['bigHeadImgUrl']
        if pd.notna(url):
            try:
                response = requests.get(url)

                # 如果请求成功 (状态码为200)
                if response.status_code == 200:
                    # 以二进制模式写入文件
                    head_img_file_path = head_img_path + '/wechat_' + name + '.jpg'
                    with open(head_img_file_path, 'wb') as file:
                        file.write(response.content)
                else:
                    print(f"文件下载失败, 状态码: {response.status_code}")

            except Exception as e:
                print(f"发生错误: {e}")


def list_image_files(folder_path):
    # 遍历文件夹，获取所有文件名
    file_names = os.listdir(folder_path)
    # 返回完整的文件路径列表
    return [os.path.join(folder_path, file) for file in file_names]


def rgb_to_grayscale(rgb):
    # 使用公式计算灰度值
    grayscale = 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]
    return grayscale


def find_edge_color(image_file_list, edge_percentage):
    dominant_color_list = []
    print('计算目标范围内的平均色')
    sleep(0.1)
    for image_file in tqdm(image_file_list):
        try:
            with Image.open(image_file).convert("RGB") as image:
                width, height = image.size

                # 只考虑图片左右两边edge_width范围的像素
                edge_width = int(width * edge_percentage)

                # 遍历目标范围的像素的RGB值，添加到edge_pixels列表里
                edge_pixels = []
                pixels = list(image.getdata())
                for x in range(edge_width):
                    for y in range(height):
                        edge_pixels.append(image.getpixel((x, y)))

                for x in range(width - edge_width, width):
                    for y in range(height):
                        edge_pixels.append(image.getpixel((x, y)))

                # 计算目标范围内的平均色
                avg_color = (
                    sum(pixel[0] for pixel in pixels) // len(pixels),
                    sum(pixel[1] for pixel in pixels) // len(pixels),
                    sum(pixel[2] for pixel in pixels) // len(pixels)
                )
                value = math.sqrt((avg_color[0])**2 + (avg_color[1])**2 + (avg_color[2])**2)

                dominant_color_list.append(value)

        except IOError:
            print("头像读取失败")

    return dominant_color_list


def joint_avatar(output_path, image_size, image_file_list, dominant_color_list):
    # 测量小头像的尺寸
    length = len(image_file_list)
    each_size = math.ceil(image_size / math.floor(math.sqrt(length)))

    # 创建画布
    x_lines = math.ceil(math.sqrt(length))
    y_lines = math.ceil(math.sqrt(length))
    image = Image.new('RGB', (each_size * x_lines, each_size * y_lines))
    x = 0
    y = 0

    # 根据边缘颜色进行排序
    sorted_dominant_color_list, image_files_rgb = sort(dominant_color_list, image_file_list)

    # 按顺序指定每张图片的位置
    print('按顺序指定每张图片的位置')
    sleep(0.1)
    for image_file in tqdm(image_files_rgb):
        try:
            with Image.open(image_file) as img:
                img = img.resize((each_size, each_size))
                image.paste(img, (x * each_size, y * each_size))
                x += 1
                if x == x_lines:
                    x = 0
                    y += 1
        except IOError:
            print(f"{image_file}头像读取失败")

    image.save(output_path + '/output.png')
    print('微信好友头像拼接完成!')


def sort(color_list, file_list):
    combined_list = list(zip(color_list, file_list))
    sorted_combined_list = sorted(combined_list, reverse=True)
    sorted_color_list, sorted_file_list = zip(*sorted_combined_list)
    return sorted_color_list, sorted_file_list


def main():
    start_time = datetime.now()
    # 参数
    config = "configs.yaml"
    with open(config, 'r', encoding='utf-8') as fin:
        configs = yaml.load(fin, Loader=yaml.FullLoader)

    # 路径
    qq_file_path = configs.get('qq_file_path')
    wechat_file_path = configs.get('wechat_file_path')
    head_img_path = configs.get('head_img_path')
    output_path = configs.get('output_path')
    log_path = configs.get('log_path')
    create_folder(head_img_path)
    create_folder(output_path)
    create_folder(log_path)

    # 下载头像
    if configs.get('qq_download_mode'):
        download_qq_head_img(qq_file_path, head_img_path)
    if configs.get('wechat_download_mode'):
        download_wechat_head_img(wechat_file_path, head_img_path)
    # 拼接大图
    if configs.get('stitch_mode'):
        image_file_list = list_image_files(head_img_path)
        dominant_color_list = find_edge_color(image_file_list, configs.get('edge_percentage'))
        joint_avatar(output_path, configs.get('image_size'), image_file_list, dominant_color_list)

    # 将参数写入日志
    end_time = datetime.now()
    spent_time = end_time - start_time
    logging.basicConfig(filename=log_path + f'/{start_time.strftime("%Y-%m-%d %H-%M-%S")}.txt',
                        level=logging.INFO, format='%(message)s')
    logging.info(f'Start Time: {start_time.strftime("%Y-%m-%d %H-%M-%S")}')
    logging.info(f'End Time: {end_time.strftime("%Y-%m-%d %H-%M-%S")}')
    logging.info(f'Elapsed Time: {spent_time}\n')
    for key, value in configs.items():
        logging.info(f'{key}: {value}')


if __name__ == "__main__":
    main()
