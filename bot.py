import asyncio
from aiogram import Dispatcher, Bot, types
import gspread
from gspread import Client, Spreadsheet, Worksheet
from lxml import etree as ET
import requests
import os

TOKEN_API = "Token"
bot = Bot(TOKEN_API)
dp = Dispatcher()

@dp.message()
async def start(message: types.Message):
    try:
        await message.answer("Ждите, мы работаем...")
        xl = []

        def show_all_values_in_ws(ws: Worksheet):
            list_of_lists = ws.get_all_values()
            for row in list_of_lists:
                xl.append(row)

        gc: Client = gspread.service_account("Confic//setings_account.json")
        sh: Spreadsheet = gc.open_by_url(message.text)
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
                for item_tag, item_info_tag in zip(tag, xl[item]):
                    if item_tag == "Images":
                        # Проверка наличия значения, чтобы <Images> не отображался как текстовый элемент
                        if item_info_tag.strip():
                            ad_element_ = ET.SubElement(ad_element, "Images")
                            for img in item_info_tag.replace("|", " ").split():
                                if "http" in img:
                                    child = ET.SubElement(ad_element_, "Image", url=img.strip())
                    elif item_info_tag == "":
                        continue
                    elif item_tag == "Description":
                        description_element = ET.SubElement(ad_element, "Description")
                        description_element.text = ET.CDATA(item_info_tag)  # Вставка CDATA секции
                    elif item_tag == "Title":
                        description_element = ET.SubElement(ad_element, "Title")
                        description_element.text = ET.CDATA(item_info_tag)  # Вставка CDATA секции
                    else:
                        child = ET.SubElement(ad_element, item_tag)
                        child.text = item_info_tag

            # Запись дерева в XML файл один раз после всех изменений с правильной кодировкой
            tree.write("output_google.xml", encoding="UTF-8", xml_declaration=True, pretty_print=True)

        async def main():
            tree, root = load_or_create_xml("output_google.xml")
            collection_data_google_sheets(tree=tree, root=root)
            await message.answer("Ваша гугл таблица была успешна переведена в output_google.xml")

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

        async def union_file():
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
            await message.answer("Данные успешна были объединены в главный файл.xml, и были сохранены в result_union.xml")
            await message.answer(os.getcwd() + "/result_union.xml")

        async def main2():
            get_xml_file()
            await union_file()

        await main()
        await main2()
        await message.delete()
        

    except:
        await message.answer("Что-то не так ):")


async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())