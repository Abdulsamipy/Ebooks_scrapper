import requests
import re
import threading
import concurrent.futures
import pandas as pd
# def get_books(session, book_num):
#     res = session.get(f"https://www.ebooks.com/sitemap/book-{book_num}.xml").text
#     get_books_url = re.findall("<loc>([\s\S]+?)</loc>", res)
#     with open('Books.txt', 'a+', encoding='utf-8') as f:
#         for url in get_books_url:
#             f.write(url + '\n')
#     with open('Books.txt', 'r+', encoding='utf-8') as a:
#         scrapped = a.readlines()
#         print(f"Scrapped: {len(scrapped)}")

# if __name__ == '__main__':
#     session = requests.Session()
#     threads = []
#     for book_num in range(1, 23):
#         t = threading.Thread(target=get_books, args=(session, book_num))
#         threads.append(t)
#         t.start()
#     for t in threads:
#         t.join()


counter = 0
with open('test.txt', 'r') as f:
    books_url = f.readlines()

r = requests.Session()


def get_book_data(book):
        gets = r.get(str(book).strip())
        get = gets.text
        if gets.status_code == 200: 
            try:
                code = re.findall('https://www\.ebooks\.com/en\-us/book/+?(\d+)[\s\S]+?', str(book).strip())
                get_price = r.get(f'https://www.ebooks.com/api/book/?bookId={code[0]}&countryCode=US').text

                try:
                    data = {
                        'tittle' : re.findall('<title>+?([\s\S]+?)</title>+?', str(get))[0],
                        'price': re.findall('"price":\{"localized_price":+?([\s\S]+)\,"price"+?', str(get_price))[0],
                        'Description': re.findall('<meta\ property="og:description"\ content="+?([\s\S]+?)"\ />+?', str(get))[0],
                        'Author': re.findall('primary\-author\-normalised\-name="+?([\s\S]+?)"+?', str(get))[0],
                        'Img': re.findall('<img\ src="+?([\s\S]+?)\?+?[\s\S]+?' , str(get))[0]
                    }
                except Exception as e:
                    
                    data = {
                        'tittle' : re.findall('<title>+?([\s\S]+?)</title>+?', str(get))[0],
                        'price': 'nul',
                        'Description': re.findall('<meta\ property="og:description"\ content="+?([\s\S]+?)"\ />+?', str(get))[0],
                        'Author': re.findall('primary\-author\-normalised\-name="+?([\s\S]+?)"+?', str(get))[0],
                        'Img': re.findall('<img\ src="+?([\s\S]+?)\?+?[\s\S]+?' , str(get))[0]
                }
            except Exception as e:
                print(f"Error on code: {code[0]}", {e})
            

            global counter
            counter = counter + 1
            print(f"Scrapped {counter}/{len(books_url)}")
            return data 
            
results = []

with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
    for data in executor.map(get_book_data, books_url):
        results.append(data)

df = pd.DataFrame(results, columns=['tittle', 'price', 'Description', 'Author', 'Img'])
df.to_excel('books_data.xlsx', index=False)
