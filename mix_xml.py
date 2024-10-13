from lxml import etree as ET
import requests
import os

# Функция для добавления CDATA в элементы с тегами Description и Title
def add_cdata_to_elements(element):
    for tag in ['Description', 'Title']:
        for elem in element.findall(f'.//{tag}'):
            # Создаем новый текстовый элемент с CDATA
            cdata = ET.CDATA(elem.text or "")
            # Создаем новый элемент с CDATA
            new_elem = ET.Element(tag)
            new_elem.text = cdata  # Добавляем CDATA в текст нового элемента
            # Заменяем старый элемент на новый
            parent = elem.getparent()
            parent.replace(elem, new_elem)

def get_xml_file():
    response = requests.get("https://baz-on.ru/export/c3451/dc3bb/avito-medusamotors.xml")
    with open("main.xml", "wb") as file:
        file.write(response.content)

def union_file():
    # Загрузка первого XML файла
    tree1 = ET.parse('main.xml')
    root1 = tree1.getroot()

    # Загрузка второго XML файла
    tree2 = ET.parse('output_google.xml')
    root2 = tree2.getroot()

    # Объединение второго файла в первый
    for child in root2:
        root1.append(child)

    # Применение фильтра на теги Description и Title
    add_cdata_to_elements(root1)

    # Сохранение объединенного XML файла
    tree1.write('result_union.xml', pretty_print=True, xml_declaration=True, encoding='UTF-8')
    print("Данные успешна были объединены в главный файл.xml, и были сохранены в result_union.xml")
    print(os.getcwd() + "/result_union.xml")

def main2():
    get_xml_file()
    union_file()

if __name__ == '__main__':
    main2()