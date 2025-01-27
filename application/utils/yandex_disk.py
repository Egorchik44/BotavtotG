
import os
import logging
import yadisk
import re
import imghdr
import traceback
from PIL import Image
from retrying import retry
from telegram import Bot

class YandexDiskAPI:
    UPLOAD_FOLDER = '/AvtoBot/'
    FILE_ID_PATTERN = r'/(d|i)/([a-zA-Z0-9_-]+)'

    def __init__(self, token):
        self.disk = yadisk.YaDisk(token=token)
        if not self.disk.check_token():
            raise ValueError("Неверный токен для Яндекс.Диска")

    def _ensure_directory_exists(self, directory_path):
        try:
            if not self.disk.exists(directory_path):
                self.disk.mkdir(directory_path)
                logging.info(f"Создана директория на Яндекс.Диске: {directory_path}")
        except yadisk.exceptions.YaDiskError as e:
            logging.error(f"Ошибка при проверке/создании директории на Яндекс.Диске: {e}")
            raise

    def is_valid_image(self, file_path):
        try:
            with Image.open(file_path) as img:
                img.verify()
            return True
        except:
            return False

    def _get_public_link(self, file_path):
        """Получить публичную ссылку на файл на Яндекс.Диске."""
        try:
            self.disk.publish(file_path)  # Публикация файла
            public_url = self.disk.get_meta(file_path).public_url
            if public_url:
                logging.info(f"Публичная ссылка для {file_path}: {public_url}")
            return public_url
        except yadisk.exceptions.YaDiskError as e:
            logging.error(f"Ошибка при получении публичной ссылки для {file_path}: {e}")
            return None
        
    @retry(stop_max_attempt_number=3, wait_fixed=2000)
    def upload_to_yandex_disk(self, local_file_path, remote_file_path):
        try:
            self.disk.upload(local_file_path, remote_file_path)
            logging.info(f"Файл успешно загружен на Яндекс.Диск: {remote_file_path}")
        except yadisk.exceptions.YaDiskError as e:
            logging.error(f"Ошибка при загрузке файла на Яндекс.Диск: {e}")
            raise

    def check_file_availability(self, file_path):
        try:
            meta = self.disk.get_meta(file_path)
            return meta.public_url is not None
        except yadisk.exceptions.YaDiskError:
            return False

    def get_download_link(self, file_path):
        try:
            return self.disk.get_download_link(file_path)
        except yadisk.exceptions.YaDiskError as e:
            logging.error(f"Ошибка при получении ссылки для скачивания: {e}")
            return None

    async def upload_to_disk(self, file_data, filename):
        file_path = f"{self.UPLOAD_FOLDER}{filename}"
        self._ensure_directory_exists(self.UPLOAD_FOLDER)

        local_file_path = f"./{filename}"
        try:
            with open(local_file_path, 'wb') as f:
                f.write(file_data)
            logging.info(f"Файл временно сохранён локально: {local_file_path}")

            if not self.is_valid_image(local_file_path):
                logging.error(f"Файл {filename} не является корректным изображением")
                return None

            if not filename.lower().endswith(('.jpg', '.jpeg', '.png')):
                logging.error(f"Неверный формат файла: {filename}")
                return None

            self.upload_to_yandex_disk(local_file_path, file_path)

            if not self.check_file_availability(file_path):
                logging.error(f"Файл {file_path} недоступен после загрузки")
                return None

            download_link = self.get_download_link(file_path)
            if not download_link:
                logging.error(f"Не удалось получить ссылку для скачивания файла {file_path}")
                return None

            return download_link

        except Exception as e:
            logging.error(f"Ошибка при обработке файла {filename}: {e}")
            logging.error(traceback.format_exc())
            return None
        finally:
            if os.path.exists(local_file_path):
                os.remove(local_file_path)
                logging.info(f"Локальная копия файла удалена: {local_file_path}")

    async def get_yandex_disk_photos(self, car_id: int):
        logging.info(f"Fetching photos for car_id {car_id}")
    
        try:
            car_info, db_photos = await get_car_info(car_id)
        
            if not db_photos:
                logging.info(f"No photos found for car_id {car_id}")
                return []
        
            photos = []
            for photo in db_photos:
                photo_url = photo[0]
            
                if not isinstance(photo_url, str):
                    logging.error(f"Invalid photo URL type: {type(photo_url)}, expected str")
                    continue

                file_id_match = re.search(self.FILE_ID_PATTERN, photo_url)
                if file_id_match:
                    link_type = file_id_match.group(1)
                    file_id = file_id_match.group(2)

                    if link_type == 'd':
                        direct_link = f"https://yadi.sk/d/{file_id}"
                    elif link_type == 'i':
                        direct_link = f"https://yadi.sk/i/{file_id}"
                
                    photos.append(direct_link)
                    logging.debug(f"Added photo URL: {direct_link}")
                else:
                    logging.warning(f"Could not extract file ID from URL: {photo_url}")
        
            logging.info(f"Successfully fetched {len(photos)} photos for car_id {car_id}")
            return photos
    
        except Exception as e:
            logging.error(f"An error occurred while fetching photos for car_id {car_id}: {e}")
            logging.error(traceback.format_exc())
            return []
