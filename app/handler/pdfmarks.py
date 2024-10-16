# coding:utf-8

import os
from datetime import date
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import zipfile

# 指定文件路径
new_path = os.path.dirname(__file__)
os.chdir(new_path)
pdfmetrics.registerFont(TTFont('msyh', './fonts/msyh.ttc'))


def create_watermark(content):
    """水印信息"""
    # 默认大小为21cm*29.7cm
    file_name = "mark.pdf"
    c = canvas.Canvas(file_name, pagesize=(50*cm, 40*cm))
    # 移动坐标原点(坐标系左下为(0,0))
    #c.translate(10*cm, 5*cm)

    # 设置字体
    c.setFont("msyh", 18)
    # 指定填充颜色
    c.setFillColorRGB(0, 1, 0)
    # 文字旋转
    c.rotate(30)
    # 指定填充颜色
    c.setFillColorRGB(0, 0, 0, 0.3)

    # 添加水印
    for i in range(10):
        for j in range(-20, 30):
            a = 6.5 * i
            b = 1.2 * (j - 1)
            c.drawString(a*cm, b*cm, content)
            c.setFillAlpha(0.1)

    # 关闭并保存pdf文件
    c.save()
    return file_name


def add_watermark(pdf_file_in, pdf_file_mark, pdf_file_out):
    """把水印添加到pdf中"""
    pdf_output = PdfWriter()
    with open(pdf_file_in, 'rb') as input_stream:
        pdf_input = PdfReader(input_stream, strict=False)

        # 获取PDF文件的页数
        pageNum = len(pdf_input.pages)
    
        # 读入水印pdf文件
        pdf_watermark = PdfReader(open(pdf_file_mark, 'rb'), strict=False)

        # 给每一页打水印
        for i in range(pageNum):
            page = pdf_input.pages[i]
            page.merge_page(pdf_watermark.pages[0])
            page.compress_content_streams()  # 压缩内容
            pdf_output.add_page(page)
        pdf_output.write(open(pdf_file_out, 'wb'))


def zip_folder(folder_path, zip_name):
    """打包压缩文件"""
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                arc_name = os.path.relpath(file_path, folder_path)
                zipf.write(file_path, arc_name)


def clear_folder(folder_path):
    """清空文件夹"""
    for fl in os.listdir(folder_path):
        file_path = os.path.join(folder_path, fl)
        if os.path.isfile(file_path):
            os.remove(file_path)


def pdf_marks(file_path, file_name, name_list):

    # 1、获取待处理pdf文件
    pdf_file_in = file_path
    file_name = file_name

    # 2、目标发送对象
    name_lists = list(name_list.replace('，', ',').split(','))
    time_marks = date.today().strftime("%Y-%m-%d")


    watermarks = [item + ' ' + time_marks + ' ' for item in name_lists]


    # 3、批量添加水印

    i = 1
    for name in name_lists:
        pdf_file_out = './output/【' + name + '】' + file_name
        watermarks = name + ' ' + time_marks
        pdf_file_mark = create_watermark(watermarks)
        add_watermark(pdf_file_in, pdf_file_mark, pdf_file_out)
        # 打印完成信息
        i = i + 1

    # 4、打包压缩文件
    folder_to_zip = './output'
    zip_name = './zips/' + file_name.split('.')[0] + '.zip'
    zip_folder(folder_to_zip, zip_name)

    # 5、清空文件夹
    clear_folder('./original')
    clear_folder('./output')


    full_path = new_path + zip_name[1:]

    return full_path
