import gspread
from gspread import Client, Spreadsheet, Worksheet
from lxml import etree as ET
from mix_xml import main2

xl = []

def show_all_values_in_ws(ws: Worksheet):
    list_of_lists = ws.get_all_values()
    for row in list_of_lists:
        xl.append(row)

gc: Client = gspread.service_account("Confic//service_account.json")
sh: Spreadsheet = gc.open_by_url("https://docs.google.com/spreadsheets/d/1hEFsXzTWI9fsX3sFom3lLWTYa65JyusGhmMUtPLwAPY/edit?gid=0#gid=0")
ws = sh.sheet1
show_all_values_in_ws(ws)

tag = xl[0]
del xl[0]

# Функция для загрузки или создания нового XML дерева
def load_or_create_xml(file):
    root = ET.Element("Ads", formatVersion="3", target="Avito.ru")
    tree = ET.ElementTree(root)
    return tree, root


def collection_data_google_sheets(tree, root):
    count_result = len(xl)
    for item in range(count_result):
        ad_element = ET.SubElement(root, "Ad")

        # Проверяем, был ли создан тег CompatibleCars
        compatible_cars_element = None

        for item_tag, item_info_tag in zip(tag, xl[item]):
            if item_tag == "Images":
                if item_info_tag.strip():
                    ad_element_ = ET.SubElement(ad_element, "Images")
                    for img in item_info_tag.replace("|", " ").split():
                        if "http" in img:
                            child = ET.SubElement(ad_element_, "Image", url=img.strip())
            elif item_info_tag == "":
                continue
            elif item_tag == "Description":
                description_element = ET.SubElement(ad_element, "Description")
                description_element.text = ET.CDATA(item_info_tag)
            elif item_tag == "Title":
                title_element = ET.SubElement(ad_element, "Title")
                title_element.text = ET.CDATA(item_info_tag)
            elif item_tag == "CompatibleCar":
                # Создаем тег CompatibleCars только один раз
                if compatible_cars_element is None:
                    compatible_cars_element = ET.SubElement(ad_element, "CompatibleCars")

                ad_element_ = ET.SubElement(compatible_cars_element, "CompatibleCar")
                for img, tag_dop in zip(item_info_tag.split("|"),
                                        ["Make", "Model", "Generation", "Modification", "BodyType", "Doors"]):
                    if img == "" or img == " ":
                        continue
                    child = ET.SubElement(ad_element_, tag_dop)
                    child.text = img.strip()
            else:
                child = ET.SubElement(ad_element, item_tag)
                child.text = item_info_tag

    tree.write("output_google.xml", encoding="UTF-8", xml_declaration=True, pretty_print=True)

def main():
    tree, root = load_or_create_xml("output_google.xml")
    collection_data_google_sheets(tree=tree, root=root)
    print("Ваша гугл таблица была успешна переведена в output_google.xml")

if __name__ == '__main__':
    main()
    main2()