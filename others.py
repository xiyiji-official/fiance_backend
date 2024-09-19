from fastapi import APIRouter, File, UploadFile, Form
from fastapi.responses import FileResponse

from typing import List

import os
import json
import uuid
from bs4 import BeautifulSoup
from docxtpl import DocxTemplate

## 引用模板，用于生成docx文件
doc = DocxTemplate("./muban.docx")  ## 请修改为自己的模板路径

## 模板内容，请更新为您的模板内容
models: str = "{time}&emsp;&emsp;&emsp;{name}<br/>会议负责人：<br/>会议分类：<br/>关注内容：<br/><br/>{url}<br/>"

router = APIRouter(
    tags=["其他API"]
)


@router.get("/reference/")
def read_reference(weekday: str | None = None):
    f = open("config.json", "r", encoding="UTF-8")
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
    # 解析文件顺序
    fileOrder = json.loads(fileOrder)


    temp_dir = str(uuid.uuid4())
    os.makedirs(temp_dir, exist_ok=True)

    saved_files = []
    for file in files:
        file_path = os.path.join(temp_dir, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        saved_files.append(file_path)

    return {"message": fileOrder}
