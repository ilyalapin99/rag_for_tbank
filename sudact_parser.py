import time
import random
import json
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from colorama import init, Fore

# цветовой вывод в консоль
init(autoreset=True)

def random_sleep(min_s=1, max_s=3):
    """Отдых чтобы не прилетел бан"""
    time.sleep(random.uniform(min_s, max_s))

def main():
    # Настройки поиска
    QUERY = "Т-банк"
    MAX_DOCS = 500
    OUTPUT_FILE = "sudact_dataset0_500.json"

    # Настройка параметров браузера Хром
    options = Options()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)

    # установка и запуск драйвера
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 15)

    all_links = []
    dataset = []
    
    try:
        # 1) Сбор ссылок на документы
        page_num = 1
        while len(all_links) < MAX_DOCS:

            search_url = f"https://sudact.ru/regular/doc/?page={page_num}&regular-txt={QUERY}"
            print(Fore.YELLOW + f"Переход на страницу {page_num} ссылок собрано {len(all_links)}")

            driver.get(search_url)
            random_sleep(2, 4)

            try: # Ожидание появления ссылок в результатах поиска
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".results h4 a")))
                links_on_page = driver.find_elements(By.CSS_SELECTOR, ".results h4 a")

                for link in links_on_page:
                    url = link.get_attribute("href")
                    if url and url not in all_links:
                        all_links.append(url)
                    if len(all_links) > MAX_DOCS:
                        break

                page_num += 1
            except:
                print((Fore.RED + "Результаты не найдены"))
                break

        # 2) Извлечение текстов из собранных ссылок
        print(Fore.CYAN + f"Ссылки ({len(all_links)})")
        success_count = 0
        for i, url in enumerate(all_links, 1):
            print(Fore.CYAN + f"[{i}/{len(all_links)}]")

            try:
                # Жду загрузки основного текстового блока
                driver.get(url)
                wait.until(EC.presence_of_element_located((By.CLASS_NAME, "h-col1")))

                try:
                    # Извлекаю заголовок
                    title = driver.find_element(By.TAG_NAME, "h1").text
                except:
                    title = ''

                try:
                    # Извлекаю основной текст решения
                    content_el = driver.find_element(By.CLASS_NAME, "h-col1"
                                                     )
                    full_text = content_el.text
                except:
                    print(Fore.RED + "Не удалось извлечь")
                    full_text = ''

                # Сохраняю только валидные документы
                if title.strip() and len(full_text.strip()) > 200:
                    case_data = {
                        "id": i,
                        "url": url,
                        "title": title,
                        "content": full_text
                    }
                    dataset.append(case_data)
                    success_count += 1
                    print(Fore.GREEN + f" Сохранено дел: {success_count}")
                else:
                    print(Fore.YELLOW + "Документ пропущен")
                print(Fore.GREEN + f"Скачано символов: {len(full_text)}")
                random_sleep(2, 4)
            except Exception as e:
                print(Fore.RED + f"Ошибка: {e}")


    except Exception as e:
        print(Fore.RED + f"Ошибка: {e}")

    # Сохраняю в JSON
    print(Fore.MAGENTA + f"Сохраняю {len(dataset)} документов в файл {OUTPUT_FILE}")
    with open(OUTPUT_FILE, "w", encoding='utf-8') as f:
        json.dump(dataset, f, ensure_ascii=False, indent=4)
        print(Fore.GREEN + "Готово")

    driver.quit()

if __name__ == '__main__':
    main()
