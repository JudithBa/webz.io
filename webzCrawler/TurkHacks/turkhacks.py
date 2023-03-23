from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver as uc
import threading
import os
import time
import json
import typer
from rich import print
app = typer.Typer(help="Awesome CLI user manager.")

with open('../configuration/config.json') as json_file:
    config = json.load(json_file)

DATA_DIR = '../data'
    # check if the directory exists and create it if it does not
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

class TH_Handler:

    def __init__(self):
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('headless')
        options.add_argument('--window-size={}x{}'.format(1280, 1024))
        # Start chrome web driver undetacted
        self.driver = uc.Chrome(use_subprocess=True, options=options)
        self.driver.set_page_load_timeout(60)
        # Start the crawling
        self.startCrawling()
        time.sleep(3)
        self.driver.close()


    def startCrawling(self): # start the crawling first login and then try to extract data from the pages and posts
        try:
            self.driver.get(config["turkacks"]["LOGIN_PAGE"])
            self.driver.implicitly_wait(5)
            # Try to acess the login page of the website and login with a user/password from config
            self.login()
        except Exception as e:
            print("LOGIN FAILED CONTINUE WITHOUT LOGIN")
            print((F'Exception occurs: {e.__str__()}'))
        try:
            self.driver.get("https://www.turkhacks.com/forum/sosyal-medya-hacking.184/")
            self.driver.implicitly_wait(10)
            # Start the crawler
            self.goOverPages()
            #self.driver.close()

        except Exception as e:
            print("SOMTHING WENT WRONG :/")
            print((F'Exception occurs: {e.__str__()}'))


    def login(self): # Enter the user name password in the login page and try to login
        try:
            print("TRY TO LOGIN :locked:")
            #print(self.driver.page_source.encode("utf-8"))
            #print(self.driver)
            email = config["turkacks"]["login_email"]
            password = config["turkacks"]["login_password"]
            self.driver.save_screenshot("turkhacks_login.png")
            email_element = self.driver.find_element(By.NAME, 'login')
            email_element.send_keys(email)  # Give email input
            password_element = self.driver.find_element(By.NAME, 'password')
            password_element.send_keys(password)  # Give password as input
            login_button = self.driver.find_element(By.CLASS_NAME, 'button')
            login_button.click()  # Send mouse click
            self.driver.implicitly_wait(10)
            print('SECCESFULLY LOGIN :thumbs_up:')
            time.sleep(3)  # Wait for 1 seconds for the page to show up
            self.driver.save_screenshot("turkhacks_login.png")
        except Exception as e:
            print("LOGIN FAILED CONTINUE WITHOUT LOGIN :warning:")

    def initDriver(self):  # Create a new Chrome driver instance with the options we set
        options = uc.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('headless')
        options.add_argument('--window-size={}x{}'.format(1280, 1024))
        driver=uc.Chrome(use_subprocess=True, options=options)
        driver.set_page_load_timeout(60)
        print("OPEN A NEW CHROME WEB DRIVER")
        return driver


    def getArticalsInRange(self, startPage, endPage,driver):  # Go over and load all the page range
        currentURL = self.driver.current_url
        thread_num = threading.get_ident()
        for page_num in range(startPage, endPage):
            print(f"Processing page {page_num} on thread {thread_num}")
            try:
                time.sleep(3)
                driver.get(f"{currentURL}sayfa-{page_num}")
                driver.implicitly_wait(10)
                #driver.save_screenshot(f"./turkhacks_thread{thread_num}_page{page_num}.png")
                self.getArticals(driver,thread_num)
                time.sleep(3)
            except Exception as e:
                print(F'Exception occurs: {e.__str__()}')
                time.sleep(3)
                continue
        # Close the new driver
        driver.close()
        return

    def goOverPages(self):  # Get the number of pages in the main page and create 2 threads that will extract the data from the pages
        try:
            totalPages = self.driver.find_elements(By.CLASS_NAME, 'pageNav-page ')
            pageNum=int(totalPages[-1].text)
            print(f"NUMBER OF PAGES THAT WILL BE PROCESS [bold] {pageNum}[/bold]  :boom:")
            # start two threads to go over all pages
            thread1 = threading.Thread(target=self.getArticalsInRange, args=(1, pageNum // 2 +1,self.initDriver()))
            thread2 = threading.Thread(target=self.getArticalsInRange,
                                       args=(pageNum // 2 + 1, pageNum + 1,self.initDriver()))
            thread1.start()
            thread2.start()
            thread1.join()
            thread2.join()
        except Exception as e:
            print(F'Exception occurs: {e.__str__()}')


    def getArticals(self,driver,thNum):      #get all the links to post in the page and access each post
        try:
            links= driver.find_elements(By.CLASS_NAME,'structItem-title')
            links_url=[]
            for link in links:
                links_url.append(link.find_element(By.TAG_NAME,"a").get_attribute("href"))
        except Exception as e:
            print(F'Exception occurs: {e.__str__()}')
            #print(links_url)
        for l in links_url:
            print(f"try extrat data from {l}")
            try:
                driver.get(l)
                driver.implicitly_wait(5)
                #driver.save_screenshot(f"./turkhacks_post_{thNum}_{l}.png")
                self.procces_single_post(driver,l,thNum)
                #driver.back()
            except Exception as e:
                print(F'Exception occurs: {e.__str__()}')
                driver.save_screenshot(f"./error_{thNum}_{l}.png")
                continue
            time.sleep(3)
        return


    def extract_data(self,driver,post_element):  #extract all the metadata from post and each comment
        user={}
        post_data={}
        user["username"] = post_element.get_attribute("data-author")
        post_data["Published Time"] = post_element.find_element(By.CSS_SELECTOR, "time.u-dt").get_attribute(
            "datetime")
        post_data["Content"] = post_element.find_element(By.CSS_SELECTOR,
                                                                 "div.message-content.js-messageContent").text
        # print(post_data)
        try:
            userExtras = driver.find_element(By.CSS_SELECTOR, "div.message-userExtras")
            pairs_element = userExtras.find_elements(By.CSS_SELECTOR, "dl.pairs.pairs--justified")

            for pair in pairs_element:
                key_element = pair.find_element(By.CSS_SELECTOR, "dt")
                value_element = pair.find_element(By.CSS_SELECTOR, "dd")

                key = key_element.text.strip()
                value = value_element.text.strip()
                user[key] = value

        except Exception as e:
                print(F'Exception occurs: {e.__str__()}')
                pass
        post_data["User Data"] = user
        #print(post_data)
        return post_data


    def procces_single_post(self,driver,link,thNum=0):     #extract all the data in the post and all his comments and same it to json file
        post_data={}
        user={}
        post_data["PageLink"]=link
        title= driver.find_element(By.CLASS_NAME, "p-title-value").text
        post_data["Title"]=title
        post_element_list = driver.find_elements(By.CLASS_NAME, "message--post")
        post_data=self.extract_data(driver,post_element_list[0])
        comments=[]
        for post in post_element_list[1:]:
            comment_data = self.extract_data(driver,post)
            comments.append(comment_data)
        if comments:
            post_data["Comments"]=comments

        #SAVE DATA
        with open(f"{DATA_DIR}/{thNum}_{title.replace('/', '_')}.json", 'w', encoding='utf8') as json_file:
            json.dump(post_data, json_file, ensure_ascii=False)
        return

@app.command()
def run():
    """
        Run the TurkHacks crawler
    """
    TH_Handler()


if __name__ == '__main__':
    app()
