from flask import Flask, render_template, request
from flask_cors import CORS
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
import logging
import csv
# import itertools
#import sys
import pandas as pd
import mysql.connector as conn
import pandas as pd
import pymysql
# from sqlalchemy import create_engine

logging.basicConfig(filename="scrapper.log" , level=logging.INFO)

application = Flask(__name__)
app = application

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
        try:
            
            SCROLL_PAUSE_TIME = 1
            CYCLES = 5
            searchString = request.form['content'].replace(" ","")
            channel_url = str(searchString)    #"https://www.youtube.com/@iNeuroniNtelligence/videos"
            options = webdriver.ChromeOptions()
            options.add_experimental_option('excludeSwitches', ['enable-logging'])
            driver = webdriver.Chrome(options=options)
            driver.get(channel_url)
            user_data = driver.find_elements(By.XPATH,'//*[@id="video-title-link"]')
            links = []
            for i in user_data:
                if i != None:
                    links.append(i.get_attribute("href"))
            l = []
            for i in links:
                if i != None:
                    l.append(i)
            wait = WebDriverWait(driver, 10)
            reviews = []
            
            for link in l:
                
                try:
                    driver.get(link)
                    
                    #print(v_id)
                    v_title = wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR,"#title > h1 > yt-formatted-string"))).text   
                    #print(v_title)
                except:
                    logging.info("Title")
                
                try:
                    button = driver.find_element(By.CSS_SELECTOR,"#expand")
                    button.click()
                except:
                    logging.info("click show more")
                
                try:
                    v_description = wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR,"#description-inline-expander > yt-formatted-string"))).text
                except:
                    logging.info("Description")
                try:
                    v_likes = wait.until(
                    EC.presence_of_element_located(
                        (By.CSS_SELECTOR,"#segmented-like-button > ytd-toggle-button-renderer > yt-button-shape > button > div.cbox.yt-spec-button-shape-next--button-text-content > span"))).text
                    print(v_likes)
                except:
                    logging.info("Number of likes")

                html = driver.find_element(By.TAG_NAME,'html')
                html.send_keys(Keys.PAGE_DOWN)  
                html.send_keys(Keys.PAGE_DOWN)  
                time.sleep(SCROLL_PAUSE_TIME * 2)
                my_dict = {"Link":link, "Title" : v_title, "Description":v_description, "Likes":v_likes}
                for i in range(CYCLES):
                    html.send_keys(Keys.END)
                    time.sleep(SCROLL_PAUSE_TIME)
                    
                    try:
                        
                        names = driver.find_elements(By.XPATH,'//*[@id="author-text"]')
                        total_names = []
                        #names = wait.until(EC.presence_of_all_elements_located(By.XPATH,'//*[@id="author-text"]'))
                        for i in names:
                            total_names.append(i.text)
                        #my_dict["Names"] = total_names
                        comments = driver.find_elements(By.XPATH,'//*[@id="content-text"]')
                        total_comments = []
                        for j in comments:
                            total_comments.append(j.text)
                        #my_dict["Comments"] = total_comments
                        my_dict1 = {total_names[i] : total_comments[i] for i in range(len(total_names))}
                        my_dict["Name and Comment"] = my_dict1

                        
                        
                        
                    except:
                        logging.info("Names")
                reviews.append(my_dict)
                break
            #print(reviews)
            try:
                df = pd.DataFrame(reviews)
                filename = channel_url.strip("https://www.youtube.com/") + ".csv"
                save_csv = df.to_csv("youtube.csv",index=True)
                print(save_csv)

            except Exception as e:
                print(e)
            
            print(df)
            return render_template('result.html', reviews=reviews[0:(len(reviews))])
            #logging.info("log my final result")
            
        except Exception as error1:
            logging.info(error1)
            return 'something is wrong'
        
        
    else:
        return render_template('index.html')
        
if __name__=="__main__":
    app.run(host='127.0.0.1', port=8000, debug=True)

