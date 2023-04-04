import logging
import json
import time

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common import TimeoutException

logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO)

url = 'https://www.blockchain.com/btc/tx/79ec6ef52c0a2468787a5f671f666cf122f68aaed11a28b15b5da55c851aee75'
source_txid = '79ec6ef52c0a2468787a5f671f666cf122f68aaed11a28b15b5da55c851aee75'
base_url = 'https://www.blockchain.com/btc/tx/'


class Crawler:

    def __init__(self):
        chrome_options = Options()
        # chrome_options.add_argument('--headless')
        chrome_options.add_argument("--start-maximized")
        chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
        chrome_options.add_argument('--disable-dev-shm-usage')  # overcome limited
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(8)

    def get_input_txids(self, txid):
        txid_list = []
        txt_json = None
        self.driver.get(base_url + txid)
        # try:
        #     WebDriverWait(self.driver, 8).until(EC.presence_of_element_located((By.CLASS_NAME, 'sc-766d58b6-0.nHcZZ')))
        # except TimeoutException:
        #     logging.error("Loading took too much time, reloading page")
        #     self.driver.refresh()
        #     time.sleep(5)
        time.sleep(1)
        self.driver.find_element(By.XPATH, f"//*[contains(text(),'JSON')]").click()  # press JSON btn
        json_elem = self.driver.find_element(By.CLASS_NAME, 'sc-6abc7442-1.eIwaHT')
        while txt_json is None:
            try:
                txt_json = json.loads(json_elem.text)
            except Exception:
                logging.error("json_loads failed, retry")
        for obj in txt_json["inputs"]:
            if obj["txid"] == '0000000000000000000000000000000000000000000000000000000000000000':
                return None
            txid_list.append(obj["txid"])
        return txid_list

    def bfs(self, source_txid):
        bfs_journey = list()  # the BFS journey result
        visited = set()  # to keep track of already visited nodes
        queue = list()  # queue

        # push the root node to the queue and mark it as visited
        queue.append(source_txid)
        visited.add(source_txid)

        # loop until the queue is empty
        while queue:
            current_node = queue.pop(0)  # pop the front node of the queue and add it to bfs_journey
            logging.info(f'Current txid: {current_node}')
            bfs_journey.append(current_node)
            current_input_list = self.get_input_txids(current_node)
            if current_input_list is None:
                print(f'CoinBase txid: {current_node}')
                break

            # check all the input nodes of the current node
            for input_node in current_input_list:
                # if the input nodes are not already visited, push them to the queue and mark them as visited
                if input_node not in visited:
                    visited.add(input_node)
                    queue.append(input_node)

        return bfs_journey

    def get_shortest_path(self, bfs_journey):
        coinbase = bfs_journey[len(bfs_journey) - 1]
        shortest_list = [coinbase]
        self.driver.get(base_url + coinbase)
        while source_txid not in shortest_list:
            txt_json = None
            time.sleep(1)
            self.driver.find_element(By.XPATH, f"//*[contains(text(),'JSON')]").click()  # press JSON btn
            json_elem = self.driver.find_element(By.CLASS_NAME, 'sc-6abc7442-1.eIwaHT')
            while txt_json is None:
                try:
                    txt_json = json.loads(json_elem.text)
                except Exception:
                    logging.error("json_loads failed, retry")
            for obj in txt_json["outputs"]:
                txid = obj["spender"]['txid']
                if txid in bfs_journey:
                    shortest_list.insert(0, txid)
                    logging.info(f'Shortest txid to base: {txid}')
                    self.driver.get(base_url + txid)
                    time.sleep(5)
                    break
        return shortest_list

    def run(self):
        logging.info("Start crawler to base")
        bfs_journey = self.bfs(source_txid)
        print(f"BFS Journey: {bfs_journey}")
        shortest_path = self.get_shortest_path(bfs_journey)
        print(f"Shortest route: {shortest_path}")
        self.driver.quit()


if __name__ == '__main__':
    Crawler().run()
