import os
import shutil
import glob
from jinja2 import Environment, FileSystemLoader
from tqdm import tqdm
import lxml.etree as ET
from acdh_tei_pyutils.tei import TeiReader

environment = Environment(loader=FileSystemLoader("./"))
template = environment.get_template("template.j2")

editions = os.path.join("data", "editions")
shutil.rmtree(editions, ignore_errors=True)
os.makedirs(editions, exist_ok=True)

headings = (
    ("Nahmen und Class", '<seg type="name">Nahmen und Class</seg>'),
    ("Firma od Raggion", '<seg type="firma">Firma od Raggion</seg>'),
    ("Procura und Firmae Trager", '<seg type="owner">Procura und Firmae Trager</seg>'),
    (
        "Oblatorien und Avocatorien",
        '<seg type="oblatorien">Oblatorien und Avocatorien</seg>',
    ),
    ("Fundi Ausweisung", '<seg type="fundi">Fundi Ausweisung</seg>'),
    (
        "Societaets Contract und Interessenten",
        '<seg type="contract">Societaets Contract und Interessenten</seg>',
    ),
    ("Heuraths Contract", '<seg type="wedding_contract">Heuraths Contract</seg>'),
    ("Anmerkungen", '<seg type="other_notes">Anmerkungen</seg>'),
)


files = glob.glob("./tei/*.xml")
for i, x in enumerate(tqdm(files)):
    doc = TeiReader(x)
    nsmap = doc.nsmap
    for y in doc.any_xpath(".//tei:surface[@xml:id]"):
        facs_id = y.attrib["{http://www.w3.org/XML/1998/namespace}id"]
        img_url = y.xpath("./tei:graphic/@url", namespaces=nsmap)[0]
        img_id = img_url.split("_")[-1].replace(".jpg", "")
        pb_node = doc.any_xpath(f'.//tei:pb[@facs="#{facs_id}"]')[0]
        ab_node = doc.any_xpath(
            f'.//tei:pb[@facs="#{facs_id}"]/following-sibling::tei:ab'
        )[0]
        ab_text = (
            ET.tostring(ab_node, encoding="utf-8")
            .decode("utf-8")
            .replace('key=", Personen ID=', 'ref="wkfm__')
            .replace('xmlns="http://www.tei-c.org/ns/1.0"', "")
            .replace("vertical-align: superscript;", "superscript")
        )
        for heading in headings:
            ab_text = ab_text.replace(heading[0], heading[1])
        page = {
            "id": f"wkfm-{img_id}",
            "img_url": img_url,
            "surface_node": ET.tostring(y, encoding="utf-8")
            .decode("utf-8")
            .replace('xmlns="http://www.tei-c.org/ns/1.0"', ""),
            "pb_node": ET.tostring(pb_node, encoding="utf-8")
            .decode("utf-8")
            .replace('xmlns="http://www.tei-c.org/ns/1.0"', ""),
            "ab_node": ab_text,
        }
        content = template.render(**page)
        with open(os.path.join(editions, f"wkfm-{img_id}.xml"), "w") as f:
            f.write(content)
