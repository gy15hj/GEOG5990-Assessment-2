Before running Assessment_2_200925978.py:
    
    - PLease ensure that 'authentication.py' and 'languages.py' are downloaded into 
      working directory.
    - Please install tweepy, textblob and tkinter within the command prompt. 
    - Please set up a Twitter API and input your access/consumers tokens and
      secrets into 'authentication.py'.
    

Running this code:
    
This models runs from a user input GUI. On running the code a window called 
'Tweet Search Parameters' will open. From here the user needs to make 4 choices:
    - select whether to search tweets by key word or username from dropdown box 
    - select the language of tweets to search for from dropdown box 
      (in ISO 639-1 language code format, en = English)
    - enter the query - the key word or username to search by 
    - enter the max number of tweets to return
    
Once the user has completed these four steps and clicked 'Okay' the programme 
will return tweets that meet the parameters and store them in a dataframe. The
code will then tidy up the tweets that are retrieved, by removing duplicates, 
before carrying out sentiment analysis on each tweet to determine how positive 
or negative it is. 

Output:
    
A text file called 'Sentiment_Summary.txt' will be written, outlining the 
details of the search as well as a summary of the sentiment analysis figures. 

A bar chart, showing the count of each sentiment class, and a pie charrt, 
showing the frequency of each sentiment class, will be displayed in the console
and will also be saved as .png files.  

Twitter API Access:

If you are unable to access a Twitter API this code can be tested using the 
csv file of tweets provided 'tweets_csv.csv'. In this case please comment out
Steps 2-6 and uncomment Step 6a before running the code. 
