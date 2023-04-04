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


def get_input_txids(driver, txid):
    txid_list = []
    txt_json = None
    driver.get(base_url + txid)
    # try:
    #     # WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, "//button[contains(text(),'JSON')]")))
    #     WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'JSON')]")))
    # except TimeoutException:
    #     logging.error("Loading took too much time, reloading page")
    #     driver.refresh()
    #     time.sleep(4)
    time.sleep(1)
    driver.find_element(By.XPATH, "//button[contains(text(),'JSON')]").click()  # press JSON btn
    json_elem = driver.find_element(By.CLASS_NAME, 'sc-6abc7442-1.eIwaHT')
    while txt_json is None:
        try:
            txt_json = json.loads(json_elem.text)
        except Exception:
            logging.error("json_loads failed, retry")
            # print('i"m in here')
    for obj in txt_json["inputs"]:
        if obj["txid"] == '0000000000000000000000000000000000000000000000000000000000000000':
            return None
        txid_list.append(obj["txid"])
    return txid_list


def bfs(driver, source_txid):
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
        current_input_list = get_input_txids(driver, current_node)
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


def get_shortest_path(driver, bfs_journey):
    coinbase = bfs_journey[len(bfs_journey)-1]
    shortest_list = [coinbase]
    driver.get(base_url + coinbase)
    # time.sleep(3)
    while source_txid not in shortest_list:
        txt_json = None
        # try:
        #     # WebDriverWait(driver, 8).until(EC.presence_of_element_located((By.XPATH, "//*[contains(text(),'JSON')]")))
        #     WebDriverWait(driver, 8).until(EC.element_to_be_clickable((By.XPATH, "//*[contains(text(),'JSON')]")))
        # except TimeoutException:
        #     logging.error("Loading took too much time, reloading page")
        #     driver.refresh()
        #     time.sleep(4)
        time.sleep(1)
        driver.find_element(By.XPATH, "//*[contains(text(),'JSON')]").click()  # press JSON btn
        json_elem = driver.find_element(By.CLASS_NAME, 'sc-6abc7442-1.eIwaHT')
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
                driver.get(base_url + txid)
                # time.sleep(5)
                break
    return shortest_list


def main():
    logging.info("Start crawler to base")
    # service = Service(executable_path="/driver/chromedriver")
    # driver = webdriver.Chrome(service=service)
    # driver = webdriver.Chrome()

    chrome_options = Options()
    # chrome_options.add_argument('--headless')
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
    chrome_options.add_argument('--disable-dev-shm-usage')  # overcome limited
    driver = webdriver.Chrome(options=chrome_options)
    driver.implicitly_wait(8)
    bfs_journey = bfs(driver, source_txid)
    print(f"BFS Journey: {bfs_journey}")
    shortest_path = get_shortest_path(driver, bfs_journey)
    print(f"Shortest route: {shortest_path}")
    driver.quit()


if __name__ == '__main__':
    main()
