import glob
import json
from acdh_tei_pyutils.tei import TeiReader

img_name_files = sorted(glob.glob("./mets/*/*_name.xml"))


imgs = {}
for x in img_name_files:
    doc_id = x.split("_")[0].split("/")[-1]
    img_doc = TeiReader(x)
    img_list = [x.text.split("_")[-1] for x in img_doc.any_xpath(".//item")]
    mets_doc = TeiReader(f"./mets/84522/{doc_id}_mets.xml")
    for i, y in enumerate(img_list):
        trans_id = mets_doc.any_xpath(".//*[@LOCTYPE='URL']")[i].attrib["{http://www.w3.org/1999/xlink}href"]
        imgs[img_list[i]] = trans_id.split("&")[0]


with open("imgs.json", "w", encoding="utf-8") as fp:
    json.dump(imgs, fp, ensure_ascii=False)