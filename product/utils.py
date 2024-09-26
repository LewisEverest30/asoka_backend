import django
from django.db.models import Q
import openpyxl
from django.core.files import File
import re

from .models import *


def import_gemstone_data(xls_path: str, photo_path: str):
    cover_file_default = File(open('fengmian.jpg', 'rb'), name='cover.jpg')
    thumbnail_file_default = File(open('suolue.png', 'rb'), name='thumbnail.jpg')
    detail_file_default = File(open('xiangxijieshao.jpg', 'rb'), name='detail.jpg')
    price_default = 333


    workbook = openpyxl.load_workbook(xls_path)
    sheet_names = workbook.sheetnames
    sheet = workbook[sheet_names[0]]  # 选择第一个工作表

    # 遍历工作表中的数据
    for row in sheet.iter_rows(min_row=2, values_only=True):  # 假设第一行是标题行，从第二行开始读取
        if all(cell is None for cell in row):  # 空行结束
            break
                
        if row[5] is not None and row[5] != '':
            price = row[5]
        else:
            price = price_default
        
        if row[8] is not None and row[8] != '':
            thumbnail = File(open(photo_path+'/'+str(row[8]), 'rb'), name=str(row[8]))
        else:
            thumbnail = thumbnail_file_default
        
        if row[10] is not None and row[10] != '':
            cover = File(open(photo_path+'/'+str(row[10]), 'rb'), name=str(row[10]))
        else:
            cover = cover_file_default
        
        if row[11] is not None and row[11] != '':
            detail = File(open(photo_path+'/'+str(row[11]), 'rb'), name=str(row[11]))
        else:
            detail = cover_file_default

        size_pattern = r'^(\d+)\D*.*'
        match_size = re.findall(size_pattern, str(row[4]))  # ['12'] 由于只有pattern一个匹配组，有多个匹配组时候是元组列表
        # print(match_size)
        size = int(match_size[0])


        new_gem = Gemstone.objects.create(  # 创建并保存模型实例
            name = row[0],
            typ = '宝石',
            symbol = row[7].replace(',', ''),
            wuxing = row[3],
            material = row[1],
            position = row[6][:2],
            size = size,
            cover = cover,
            thumbnail = thumbnail,
            detail = detail,
            loc = row[2],
            intro = row[9],
            price = price, 
        )