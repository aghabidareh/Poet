import requests
from bs4 import BeautifulSoup
import concurrent.futures

base_url = "https://ganjoor.net"

def get_chapters():
    response = requests.get(f"{base_url}/ferdousi/shahname")
    soup = BeautifulSoup(response.text, "html.parser")
    chapters = soup.select(".part-title-block a")
    return [base_url + chapter['href'] for chapter in chapters]


def get_sections(chapter_url):
    response = requests.get(chapter_url)
    soup = BeautifulSoup(response.text, "html.parser")
    sections = soup.select(".poem-excerpt a")
    return [base_url + section['href'] for section in sections]


def get_poems(section_url):
    response = requests.get(section_url)
    soup = BeautifulSoup(response.text, "html.parser")
    poems = soup.select(".m1, .m2")
    return [poem.text.strip() for poem in poems]


def save_poems(poems, filename="../poems.txt"):
    with open(filename, "w", encoding="utf-8") as file:
        file.write("\n".join(poems))


def main():
    print("در حال دریافت لیست سرفصل‌ها...")
    chapters = get_chapters()
    all_poems = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = []

        for chapter_url in chapters:
            futures.append(executor.submit(get_sections, chapter_url))

        sections_list = [future.result() for future in concurrent.futures.as_completed(futures)]

        futures.clear()

        for sections in sections_list:
            for section_url in sections:
                futures.append(executor.submit(get_poems, section_url))

        all_poems = []
        for future in concurrent.futures.as_completed(futures):
            all_poems.extend(future.result())

    print("در حال ذخیره اطلاعات...")
    save_poems(all_poems)
    print(f"عملیات با موفقیت انجام شد! {len(all_poems)} بیت استخراج شد.")


if __name__ == "__main__":
    main()