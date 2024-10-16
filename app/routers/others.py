from pathlib import Path
from fastapi import APIRouter, File, HTTPException, UploadFile, Form, Query
from fastapi.responses import FileResponse

from app.setting import settings

from typing import List

import os
import shutil
import json
import uuid
import requests
from bs4 import BeautifulSoup
from docxtpl import DocxTemplate
from app.handler.pdfmarks import pdf_marks

## 引用模板，用于生成docx文件
doc = DocxTemplate(settings.template)  ## 请修改为自己的模板路径

## 模板内容，请更新为您的模板内容
models: str = "{time}&emsp;&emsp;&emsp;{name}<br/>会议负责人：<br/>会议分类：<br/>关注内容：<br/><br/>{url}<br/>"

router = APIRouter(tags=["其他API"])


@router.get("/reference/")
def read_reference(weekday: str | None = None):
    f = open(settings.config, "r", encoding="UTF-8")
    config = json.load(f)
    if weekday is not None:
        for i in config["reference"]:
            if i["name"] == weekday:
                data = i["content"]
                return data
    else:
        data = config["reference"]
        return data


@router.post("/meeting/settings/")
def settings(item: dict):
    global models
    models = item["item"]
    return "成功设置"


@router.post("/meeting/")
def meeting(item: dict):
    data = item["item"]
    soup = BeautifulSoup(data, "html.parser")
    table = soup.find("table")
    temple = []
    try:
        for row in table.find_all("tr"):
            cell = row.find_all("td")
            try:
                time = (  # noqa: F841
                    (cell[0].text)
                    .replace(" ", "")
                    .replace("\n", "")
                    .replace(":", "：")
                    .split("-")[0]
                )
            except Exception as e:  # noqa: F841
                time = ""  # noqa: F841
            try:
                name = (cell[1].text).replace(" ", "").replace("\n", "").split("【")[0]  # noqa: F841
            except Exception as e:  # noqa: F841
                name = ""  # noqa: F841
            try:
                url = cell[2].find("a").get("href")  # noqa: F841
            except Exception as e:  # noqa: F841
                url = ""  # noqa: F841
            temple.append(eval(f'f"{models}"'))
    except Exception as e:
        print(e)
        return {"data": "没有可解析内容"}
    return {"data": temple}


@router.post("/render/")
def renderDocx(item: dict):
    doc.render(item)
    doc.save("result.docx")
    return FileResponse("result.docx")


@router.post("/mergefiles/")
async def mergefiles(files: List[UploadFile] = File(...), fileOrder: str = Form(...)):
    file_dir = (
        Path(__file__).resolve().parent.parent
    )  ## XXX: 不知道为什么不能修改为settings.current_dir
    # 解析文件顺序
    fileOrder = json.loads(fileOrder)

    temp_dir = str(uuid.uuid4())
    temp_path = file_dir.joinpath(temp_dir)
    os.makedirs(temp_path, exist_ok=True)

    saved_files = []
    for file in files:
        file_path = os.path.join(temp_path, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        saved_files.append(str(file_path))
    url = "http://localhost:5000/Merge"
    data = {
        "pathList": saved_files,
        "additionalString": str(file_dir.joinpath(f"output/{temp_dir}.pptx")),
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        if temp_path.exists():
            shutil.rmtree(temp_path)
        return response.json()
    else:
        return HTTPException(status_code=400, detail="合并失败")

@router.post("/pdfmarks/")
async def pdfmarks(files: UploadFile = File(...), fileOrder: str = Form(...)):
    # 获取original文件夹的路径
    original_dir = Path(__file__).parent.parent / "handler" / "original"

    # 获取文件
    file_name = files.filename
    file_path = os.path.join(original_dir, file_name)

    # 保存上传的文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(files.file, buffer)
    print(file_path)

    # 获取姓名列表
    name_list = fileOrder

    # 调用pdf_marks函数批量添加水印
    try:
        zip_path = pdf_marks(file_path, file_name, name_list)
        print(zip_path)
        return {"message": "success", "path": zip_path}
    except Exception as e:
        # 返回错误响应
        raise HTTPException(status_code=500, detail=f"Error processing file: {e}")


@router.get("/download_pptx/")
async def download_pptx(file_path: str = Query(..., description="PPTX文件的绝对路径")):
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")

    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=os.path.basename(file_path),
    )
