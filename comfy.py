from aiohttp_retry import ExponentialRetry, RetryClient
import aiohttp 
import random 
import asyncio
import csv


class ProxyAndUserAgent: 
    @classmethod 
    def get_random_user_agent(cls): 
        with open(r"D:\Python\user_agent.txt") as file: 
            user_agents = [ua.strip() for ua in file.readlines()] 
            return random.choice(user_agents)
        
    @classmethod 
    def get_random_proxy(cls): 
        with open(r"D:\Python\proxy.txt") as file: 
            proxies = [pr.strip() for pr in file.readlines()]
            params_proxy = random.choice(proxies).split(":")
            return f"http://{params_proxy[2]}:{params_proxy[3]}@{params_proxy[0]}:{params_proxy[1]}"


class WorkWithCSV: 
    @classmethod
    def create_csv_file(cls): 
        with open("comfy-parser.csv", "w", encoding="utf-8-sig", newline="") as file: 
            writer = csv.writer(file, delimiter=";")
            writer.writerow([
                "ID", "NAME", "URL", "BRAND_NAME", "PRICE"
            ])

    @classmethod 
    def add_to_file(cls, id, name, url, brand_name, price): 
        with open("comfy-parser.csv", "a", encoding="utf-8-sig", newline="") as file: 
            writer = csv.writer(file, delimiter=";")
            writer.writerow([
                id, name, url, brand_name, price
            ])


class ComfyParser: 
    def __init__(self, product_name): 
        self.product_name = product_name
        WorkWithCSV.create_csv_file() 

    async def parse_link_product(self): 
        fake_ua = ProxyAndUserAgent.get_random_user_agent()

        headers = {
            'authority': 'comfy.ua',
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'content-type': 'application/json',
            'referer': 'https://comfy.ua/ua/search/cat__17063/?q=lego&p=3',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': fake_ua,
            'x-ray-id': '',
            'x-session-id': '',
        }

        params = {
            'query': self.product_name,
            'cityId': '506',
            'storeId': '5',
            'filter': '',
            'size': '50',
            'page': '0',
            'sortBy': '',
            'order': '',
            'showMarkdown': 'true',
        }

        async with aiohttp.ClientSession() as session: 
            while True: 
                params["page"] = str(int(params["page"]) + 1)

                retry_options = ExponentialRetry(attempts=5) 
                retry_client = RetryClient(raise_for_status=False, retry_options=retry_options, client_session=session, start_timeout=0.5, factor=3.0)

                proxy = ProxyAndUserAgent.get_random_proxy()

                async with retry_client.get("https://comfy.ua/api/products/catalogsearch", headers=headers, params=params, proxy=proxy) as response:                    
                    try:
                        res_json = await response.json(content_type=None)
                    except: 
                        print("403")
                        break
                    
                    if res_json["items"] == []:
                        break

                    for item in res_json["items"]: 
                        id = item["id"]
                        name = item["name"].replace(",", "")
                        url = "https://comfy.ua/ua" + item["url"]
                        brand_name = item["brand"]["name"]
                        price = item["prices"]["price"]

                        WorkWithCSV.add_to_file(id, name, url, brand_name, price)

                    print(f"[INFO] Page done: {params['page']}")
            print("[INFO] Done!")


if __name__ == "__main__": 
    product_name = input("your product >>> ")
    cp = ComfyParser(product_name) 
    asyncio.run(cp.parse_link_product())
    
