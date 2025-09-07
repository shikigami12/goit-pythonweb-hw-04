
"""
Асинхронний скрипт для сортування файлів за розширеннями.

Цей скрипт рекурсивно сканує вихідну папку, копіює всі знайдені файли
в цільову папку, розподіляючи їх по підпапках, назви яких відповідають
розширенню файлів.

Використання:
python sort.py --source /шлях/до/вихідної/папки --output /шлях/до/цільової/папки
"""
import argparse
import asyncio
import logging
from aiopath import AsyncPath
from aiofiles import open as aio_open
from shutil import copyfile

# Налаштування логування для виводу інформації та помилок
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

async def read_folder(source_folder: AsyncPath, output_folder: AsyncPath):
    """
    Асинхронно та рекурсивно читає вміст вихідної папки, знаходить усі файли
    і створює завдання на їх копіювання.
    """
    tasks = []
    try:
        async for item in source_folder.glob('**/*'):
            if await item.is_file():
                tasks.append(asyncio.create_task(copy_file(item, output_folder)))
    except Exception as e:
        logging.error(f"Помилка під час читання папки {source_folder}: {e}")
        return

    if tasks:
        await asyncio.gather(*tasks)
        logging.info(f"Успішно оброблено {len(tasks)} файлів.")
    else:
        logging.info("Не знайдено файлів для копіювання.")

async def copy_file(file_path: AsyncPath, output_folder: AsyncPath):
    """
    Асинхронно копіює файл у відповідну підпапку в цільовій директорії.
    Підпапка створюється на основі розширення файлу.
    """
    try:
        extension = file_path.suffix.lstrip('.').lower()
        if not extension:
            extension = 'no_extension'

        destination_dir = output_folder / extension
        await destination_dir.mkdir(exist_ok=True, parents=True)

        destination_path = destination_dir / file_path.name

        # Використовуємо асинхронні операції для читання та запису
        async with aio_open(file_path, 'rb') as f_in:
            content = await f_in.read()
            async with aio_open(destination_path, 'wb') as f_out:
                await f_out.write(content)

        logging.info(f"Скопійовано {file_path} до {destination_path}")
    except Exception as e:
        logging.error(f"Не вдалося скопіювати файл {file_path}: {e}")

async def main():
    """
    Головна асинхронна функція, що парсить аргументи та запускає процес сортування.
    """
    parser = argparse.ArgumentParser(
        description="Асинхронне сортування файлів за розширеннями."
    )
    parser.add_argument(
        "--source", "-s",
        required=True,
        help="Вихідна папка з файлами для сортування."
    )
    parser.add_argument(
        "--output", "-o",
        default="dist",
        help="Папка призначення для відсортованих файлів (за замовчуванням: dist)."
    )

    args = parser.parse_args()

    source_folder = AsyncPath(args.source)
    output_folder = AsyncPath(args.output)

    if not await source_folder.is_dir():
        logging.error(f"Вихідна папка не існує: {source_folder}")
        return

    logging.info(f"Початок сортування з '{source_folder}' до '{output_folder}'")
    await read_folder(source_folder, output_folder)
    logging.info("Сортування завершено.")

if __name__ == "__main__":
    # Для запуску асинхронного коду потрібні бібліотеки aiopath та aiofiles
    # Встановіть їх за допомогою pip:
    # pip install aiopath aiofiles
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Процес перервано користувачем.")

