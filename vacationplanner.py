#!/path/to/env/python3



####### Will catch tracebacks and errors
import cgitb
cgitb.enable()



######## Set up logger
import logging 

# Set level
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create file handler
handler = logging.FileHandler('log.log')
handler.setLevel(logging.DEBUG)

# Create a logging format
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handlers to the logger
logger.addHandler(handler)



######## Print HTML 
print("Content-Type: text/html")
print()
print("<html>")
print('<title>Redirecting... </title>')
print("<main>")



######## Take the review and season information in from the POST
import cgi
import re
form = cgi.FieldStorage()
review = form["review"].value
review = review.lower()
review = re.sub('[^A-Za-z0-9]+', ' ', review)
review = [review]
season = form["season"].value
season = re.sub('[^A-Za-z0-9]+', ' ', season)


######## Open pickles
import pickle

with open('clf_s1.pickle', 'rb') as file_:
    clf_s1 = pickle.load(file_)

with open('clf_s2.pickle', 'rb') as file_:
    clf_s2 = pickle.load(file_)
    
with open('clf_s3.pickle', 'rb') as file_:
    clf_s3 = pickle.load(file_)
    
with open('clf_s4.pickle', 'rb') as file_:
    clf_s4 = pickle.load(file_)
    
with open('vectorizer.pickle', 'rb') as file_:
    vectorizer = pickle.load(file_)



######## This file contains only hotel name and address, from the Datafiniti set on Kaggle
import pandas as pd
df = pd.read_csv('path/to/file/df.csv')



######## Def suggestion function
def suggest_destination(review, season):
    X_test = vectorizer.transform(review).toarray()
    if season == 'Spring':
        prediction = clf_s1.predict(X_test)[0]
    elif season == 'Summer':
        prediction = clf_s2.predict(X_test)[0]
    elif season == 'Fall':
        prediction = clf_s3.predict(X_test)[0]
    else:
        prediction = clf_s4.predict(X_test)[0]
    df_answer = df[df['hotel_name'] == prediction][['hotel_name', 'hotel_address']].head(1)
    df_answer = df_answer.reset_index(drop=True)
    answer = df_answer['hotel_name'][0], df_answer['hotel_address'][0]
    answer_url_str = str(answer[0]).replace(" ", "%20")+" located at "+str(answer[1]).replace(" ", "%20")
    answer = answer[0]+" located at "+answer[1]
    answer_url = "https://www.google.com/search?q={}".format(answer_url_str)
    return answer, answer_url

  

######## Redirect
if __name__ == '__main__':
    ######## Call for answer
    answer, answer_url = suggest_destination(review, season)
    ######## Log IP, review, season, answer, and URL
    import os
    IPAddr = os.environ['REMOTE_ADDR']
    logger.debug((IPAddr, review, season, answer, answer_url))

    ######## Redirect
    redirectURL = "http://gmayock.com/py/vacation/default.php?answer={}&answer_url={}".format(answer, answer_url)
    print('<meta http-equiv="refresh" content="0;url=%s" />' % redirectURL) 
    print('Location: %s' % redirectURL)
    print('Redirecting... <a href="%s">Click here if you are not redirected</a>' % redirectURL)
