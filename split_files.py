import os
import shutil
import glob
import lxml.etree as ET

from jinja2 import Environment, FileSystemLoader
from tqdm import tqdm
from acdh_tei_pyutils.tei import TeiReader
from saxonche import PySaxonProcessor


environment = Environment(loader=FileSystemLoader("./"))
template = environment.get_template("template.j2")
arche_base = "https://id.acdh.oeaw.ac.at/wkfm/"
editions = os.path.join("data", "editions")
shutil.rmtree(editions, ignore_errors=True)
os.makedirs(editions, exist_ok=True)
XSLT = "./fix_comment.xsl"

headings = (
    ("/>Nahmen und Class", '/><seg type="orighead__name">Nahmen und Class</seg>'),
    ("/>Firma od Raggion", '/><seg type="orighead__firma">Firma od Raggion</seg>'),
    ("/>Procura und Firmae Trager", '/><seg type="orighead__owner">Procura und Firmae Trager</seg>'),
    (
        "/>Oblatorien und Avocatorien",
        '/><seg type="orighead__oblatorien">Oblatorien und Avocatorien</seg>',
    ),
    ("/>Fundi Ausweisung", '/><seg type="orighead__fundi">Fundi Ausweisung</seg>'),
    (
        "/>Societaets Contract und Interessenten",
        '/><seg type="orighead__contract">Societaets Contract und Interessenten</seg>',
    ),
    (
        "/>Societats Contract und Interessenten",
        '/><seg type="orighead__contract">Societats Contract und Interessenten</seg>',
    ),
    ("/>Heuraths Contract", '/><seg type="orighead__wedding_contract">Heuraths Contract</seg>'),
    ("/>Heuraths=Contract", '/><seg type="orighead__wedding_contract">Heuraths=Contract</seg>'),
    ("/>Anmerkungen", '/><seg type="orighead__other_notes">Anmerkungen</seg>'),
)


files = glob.glob("./tei/*/*.xml")
for i, x in enumerate(tqdm(files)):
    col_id = x.split('/')[-2]
    doc_id = os.path.split(x)[-1].replace('.xml', '')
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
        ab_text = ab_text.replace('ref="wkfm', 'ref="#wkfm')
        page = {
            "id": f"wkfm-{img_id}",
            "col_id": col_id,
            "doc_id": doc_id,
            "img_id": img_id,
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
        with PySaxonProcessor(license=False) as proc:
            xsltproc = proc.new_xslt30_processor()
            document = proc.parse_xml(xml_text=content)
            executable = xsltproc.compile_stylesheet(stylesheet_file=XSLT)
            output = executable.transform_to_string(xdm_node=document).replace(r"\u0022", "")
            with open(os.path.join(editions, f"wkfm-{img_id}.xml"), "w") as f:
                f.write(output)

files = glob.glob('./data/editions/*xml')
print("fixing facs")
for x in tqdm(files):
    doc = TeiReader(x)
    facs_url = doc.any_xpath(".//tei:graphic/@url")[0]
    pb = doc.any_xpath(".//tei:pb")[0]
    pb.attrib["corresp"] = f"{arche_base}{facs_url}"
    doc.tree_to_file(x)