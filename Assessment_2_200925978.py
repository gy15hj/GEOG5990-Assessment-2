# -*- coding: utf-8 -*-

"""
Created on Tue Jan  8 09:34:19 2019
@author: Harriet
"""

'''
Before running this code:
    
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
'''
##############################################################################
######################## Step 1: Import Modules/Packages  ####################
##############################################################################

import tweepy 
import pandas
import matplotlib.pyplot as plt
import numpy as np
from textblob import TextBlob
import datetime
from Language_Library import lang_dict
from authentication import auth
from tkinter import * #do i need to import everything???


##############################################################################
##################### Step 2: API Access & Authentication ####################
##############################################################################

# Passing in auth information from authentication.py to access API 
api = tweepy.API(auth)

##############################################################################
##################### Step 3: Generate GUI for user input ####################
##############################################################################

# Initialise main tkinter window, set title and size.  
root = Tk()
root.title("Twitter Search Parameters")
root.geometry("500x140")


# Add a grid to aid layout of widgets
mainframe = Frame(root)
mainframe.grid(column=0,row=0)
mainframe.columnconfigure(0, weight =  1)
mainframe.rowconfigure(0, weight = 1)
 
# Create a Tkinter variable for 'search by' input.  
# Create dictionary containing options for dropdown menu and set default option.
search_input = StringVar(root)
choices = {'Word','Username'}
search_input.set('Word') 

#Create dropdown menu, set label and postions within grid.  
SearchMenu = OptionMenu(mainframe, search_input, *choices)
Label(mainframe, text="Search by...").grid(row = 1, column = 0)
SearchMenu.grid(row = 1, column =1)

# Create a Tkinter variable for language input.  
# Access dictionary containing optionsfor dropdown menu.
lang_input = StringVar(root)
language_choices = lang_dict
lang_input.set('en')

#Create dropdown menu, set label and postions within grid. 
LangMenu = OptionMenu(mainframe, lang_input, *language_choices)
Label(mainframe, text="Language").grid(row = 2, column = 0)
LangMenu.grid(row = 2, column =1)

# Create text entry field, set label and position within grid.  
query_input = Entry(root)
Label(root, text = "Search Term/Username").grid(row = 3, column = 0)
query_input.grid(row = 3, column = 1)
#query_input.insert(INSERT, "Brexit") #preset input for ease when testing code.

# Create text entry field, set label and position within grid.
count_input = Entry(root)
Label(root, text = "No. of Tweets").grid(row = 5, column = 0)
count_input.grid(row = 5, column = 1)
#count_input.insert(INSERT, "30") #preset input for ease when testing code.

# Create buttons, one to confirm options and another to close the pop up.
Button(root, text='Close', command= quit).grid(row = 6, column = 0)
Button(root, text='Okay', command= root.quit).grid(row = 6, column = 1)

root.mainloop()


if len(query_input.get()) == 0:
    '''
    If nothing has been inputed by user into 'query_input' entry object, print
    warning. 
    '''
    print ("!! Please enter a search term/username !!")
if len(count_input.get()) == 0:
    '''
    If nothing has been inputed by user into 'count_input' entry object, print
    warning. 
    '''
    print ("!! Please enter number of tweets to return !!")
else:
    print ("Thank you, please wait...")


#print (query_input.get()) # Print to test what .get() returns when input is
#print (count_input.get()) # left blank in GUI - for developement of code to 
                           # print warning if user doesn't enter a value.  
                           
    
#if query_input.get() == None: 
#    print ("Please enter a search term/username")
#elif count_input .get() == None:
#    print ("Please enter number of tweets to return")
#else:
#    print ("Thank you, please wait")
                           
def quit():
    '''
    Objective: 
    Function that closes the GUI when necessary.  
    
    Input:
    root =  tkinter GUI 
    '''
    global root 
    root.destroy()
    
##############################################################################
################## Step 4: Link Variables to User Input ######################
##############################################################################

# First attempt at assigning user inputs to search criteria variables
#search_by = search_input
#query = query_input
#language = lang_input
#n_tweets = count_input

# Code not running - Print to test what user inputs return. 
# Outputs not retuning that was entered by user - just the tkinter variables 
#print ("Search_input", search_input) #Output: PY_VAR60
#print (type(search_input)) # Output: tkinter.StringVar

# Use .get to return contents of input variables. 
# Print to check data type of Tkinter variables. 
#print (type(search_input.get())) # Output: String 
#print (type(query_input.get())) # Output: String 
#print (type(lang_input.get())) # Output: String 
#print (type(count_input.get())) # Output: String 

# Assign tkinter variables and convert to format required by tweepy parameters
# where necesssary.  
search_by = search_input.get()
query = query_input.get()
language = lang_input.get()
n_tweets = (int(count_input.get()))

# Assign count_input to variable without converting to integer as needed in 
# string format when writing to text file (Step 11). 
n_tweets_str = (count_input.get())

# Look up name of language code selected within GUI from dictionary 
#(for use in Step 11)
language_name = lang_dict[lang_input.get()]

##############################################################################
############### Step 5: Carry out Search and Store Tweets ####################
##############################################################################

results = []


def twitter_search():
    '''
    Objective:
    Function uses .Cursor property of tweepy package to interate through the 
    number of tweets as defined in 'items' based on the parameters set within
    the GUI. Stores object 'tweet' in 'results' list.  
    
    The .now property of datetime package used to record current time at the 
    time of search. The .strftime method is used to create a string of the time 
    recorded in specified format to resolves issues writing time to text file.
    
    Output: 
    results = List containing tweets in JSON format. 
    '''

    search_datetime = datetime.datetime.now().strftime("%d-%m-%Y %H:%M")

    if search_by == 'Word':
        '''
        The users 'search by' selection in the GUI is used to determine whether 
        api.search or api.user_timeline method is used to carry out the search.  
        '''
        for tweet in tweepy.Cursor (api.search, q = query, lang = language).items(n_tweets): 
            results.append(tweet)
    else:
        for tweet in tweepy.Cursor (api.user_timeline, id=query,).items(n_tweets): 
            results.append(tweet)

twitter_search() 

#print (type(results)) # Print to test that 'results' list is as expected and
#print (len(results))  # that the correct number of tweets have been retrieved.                    

def tweets_df(results):
    '''
    Objective:
    Function to create dataframe with labelled columns containing different 
    JSON elements of each 'tweet' object
    
    Input:
    results = list to which each tweet object has been appended, containing all
              JSON elements of said tweet object.  
        
    Output:        
    data_set = data frame populated with tweets and associated data     
    '''
    id_list = [tweet.id for tweet  in results]
    data_set = pandas.DataFrame(id_list, columns = ["id"])
    
    data_set["text"] = [tweet.text for tweet in results]
    data_set["created_at"] = [tweet.created_at for tweet in results]
    data_set["retweet_count"] = [tweet.retweet_count for tweet in results]
    data_set["user_screen_name"] = [tweet.author.screen_name for tweet in results]
    data_set["user_followers_count"] = [tweet.author.followers_count for tweet in results]
    data_set["user_location"] = [tweet.author.location for tweet in results]
    
    return data_set

data_set = tweets_df(results)

#print (data_set.text[0:10]) # Print first 10 rows of 'text' column to check
                             # that the content fits search criteria. 

#print (data_set.shape[0]) #Print number of rows in data_set.
#print (data_set['user_screen_name'].value_counts()) #Print count of values. 
# Test - if searching by username, the number of rows and the count of the 
# username should be the same i.e all tweets in dataframe are by the same user. 
                             
                             
##############################################################################
###################### Step 6: Remove Duplicate Tweets #######################
##############################################################################

text = data_set["text"]

def delete_duplicates():
    '''
    Objective:
    Function to return data_set with duplicate tweets removed.  
    
    Input:
    text = data_set column containg text element of tweets.
    
    Output:
    data_set = data frame containing tweets from search, with duplicates removed
    '''   
    for i in range(0,len(text)):
        txt = ' '.join(word for word in text[i] .split() if not word.startswith('https:'))
        data_set.set_value(i, 'text2', txt)
  
    data_set.drop_duplicates('text2', inplace=True)
    data_set.reset_index(drop = True, inplace=True)
    data_set.drop('text', axis = 1, inplace = True)
    data_set.rename(columns={'text2': 'text'}, inplace=True)

# Count rows within data_set dataframe to determine how many tweets remain 
# after removing duplicates. Convert to string for use in Step 11.
tweet_count = data_set.shape[0]
tweet_count_str = (str(tweet_count))

# Write data frame containing tweets to csv file for users without API access.
#data_set.to_csv('/200925978_Assess_2/tweets_csv.csv')


##############################################################################
################ Step 6a: Read in CSV file containing tweets #################
##############################################################################

'''
# Set parameters/outputs to those in place when CSV file was created. 

search_by = 'Word'
query = "Brexit" 
language = 'en'
language_name = lang_dict[language]
n_tweets = 150
n_tweets_str = (str(n_tweets))
search_datetime = '09-01-2019 10:34'
tweet_count_str = '126' 

# Read in CSV file and assign to 'data_set'.  

data_set = pandas.read_csv('tweets_csv.csv')

#data_set #show data_set to check csv has been read in correctly.  
'''

##############################################################################
######################### Step 7: Sentiment Analysis #########################
##############################################################################

text = data_set["text"]

def sentiment_calc():
    '''
    Objective:
    Function uses sentiment.polarity property within the TextBlob package to 
    calculate the polarity of each tweet and stores value in new column within 
    'data_set'. Tweets classified as 'positive', 'negative' or 'neutral' 
    depending on value and clasfiication stored an additional 'Sentiment Class'
    column. 
    
    Input:
    text = text column of data_set which stores the main text of each tweet
        
    Output: 
    Additonal 'Sentiment'and 'Sentiment Class' columns in 'data_set' dataframe. 
    '''
    for i in range(0,len(text)):
        textB = TextBlob(text[i])
        sentiment = textB.sentiment.polarity 
        data_set.set_value(i, 'Sentiment',sentiment)
        if sentiment <0.00:
            SentimentClass = 'Negative'
            data_set.set_value(i, 'SentimentClass', SentimentClass )
        elif sentiment >0.00:
            SentimentClass = 'Positive'
            data_set.set_value(i, 'SentimentClass', SentimentClass )
        else:
            SentimentClass = 'Neutral'
            data_set.set_value(i, 'SentimentClass', SentimentClass )

# Code runs but gives warning:
# FutureWarning: set_value is deprecated and will be removed in a future release. 
# Please use .at[] or .iat[] accessors instead. 
# Attempted to use .at[] as per the relevant documentation but was unsuccessful. 
        
#    for i in range(0,len(text)):
#        textB = TextBlob(text[i])
#        sentiment = textB.sentiment.polarity 
#        data_set.at['Sentiment'] = sentiment
#        if sentiment <0.00:
#            SentimentClass = 'Negative'
#            data_set.at['SentimentClass'] = SentimentClass
#        elif sentiment >0.00:
#            SentimentClass = 'Positive'
#            data_set.at['SentimentClass'] = SentimentClass 
#        else:
#            SentimentClass = 'Neutral'
#            data_set.at['SentimentClass'] = SentimentClass 
            
sentiment_calc() 

#print (data_set.Sentiment[1])
#print (data_set.SentimentClass[1]) #Print to test.  

##############################################################################
###################### Step 8: Create Summary Dataframe ######################
##############################################################################
  
# When printing to text file, decimal points kept changing and altering the 
# alignment of the summary table, having written to file witout index column. 
# Wanted to set fixed decimal places for each value - first attempt returned 
# error as .round is a property of pandas dataframe and I was trying to call 
# to something that was not yet in a dataframe. 

#summary = pandas.DataFrame()
#summary["Mean"] = [data_set.Sentiment.mean()].round(2)
#summary["Max"] = [data_set.Sentiment.max()].round(1)
#summary["Min"] = [data_set.Sentiment.min()].round(1)


def summary_df(data_set):
    
    '''
    Objective:
    Function to calculate the mean, maximum and minimum sentiment values, round 
    values to suitable decimal place and store in a dataframe. 
    
    Input:
    data_set = data frame containing tweets and calculated sentiment values in 
    "Sentiment" column.  
   
    Output:
    summary = data frame containing mean, maximum and minimum sentiment values 
    of tweets returned from search.  
    '''
    
    summary = pandas.DataFrame()
     
    summary["Mean"] = [data_set.Sentiment.mean()]
    summary["Max"] = [data_set.Sentiment.max()]
    summary["Min"] = [data_set.Sentiment.min()]
    
    summary["Mean"] = summary["Mean"].round(2)
    summary["Max"] = summary["Max"].round(1)
    summary["Min"] = summary["Min"].round(1)
    
    return summary 

summary = summary_df(data_set)

#print(summary) # Test that summary is as expected.  

##############################################################################
################### Step 9: Sentiment Count & Bar Chart  #####################
##############################################################################

#sentiment_count = data_set['SentimentClass'].value_counts()

#print(data_set.SentimentClass) # Print (with items set to 10) to check 
                                # count of each sentiment class against calc.
#print(sentiment_count) # Print to check sentiment_count returns correct counts
                        # Realised that the order in which the three classes 
                        # were printed (and therfore being stored) changed 
                        # unpredictably each time code was run.

sentiment_count = data_set['SentimentClass'].value_counts(sort= True)

#print(sentiment_count) # Test to check sentiment_count returns correct counts
                        # and that setting 'sort' parameter to 'True' has ensured 
                        # that the three counts are always stored in ascending
                        # order - useful when plotting bar/pie charts.  

def bar_chart(sentiment_count):
    '''
    Objective:
    Function that uses matplotlib (plt) to plot a bar chart of the count of
    each of the three sentiment classes within the sample of tweets.  
    
    Input: 
    sentiment_count = variable holds the count of each sentiment class in 
    the 'Sentiment Class'  column of 'data_set' calculated using .value_count.  
    
    Output:
    Bar chart displayed in console and saved in .png format. 
    '''
    index = np.arange(len(sentiment_count))
    plt.bar(index, sentiment_count, color = '#7EC0EE')
    plt.xlabel('Sentiment Class', fontsize=10)
    plt.ylabel('Number of Tweets', fontsize=10)
    plt.xticks(index, sentiment_count.index, fontsize=10, rotation=30)
    if search_by == 'Word':
        '''
        Title of bar chart is dependent on the choice made by user within GUI
        to search by either 'Word' or 'User'. 
        '''
        plt.title("Sentiment Count of Tweets Containing Search Term " + '"' + query + '"')
    else:
        plt.title("Sentiment Count of Tweets by " + '"' + query + '"')
    plt.savefig('barchart.png', bbox_inches = 'tight')
    plt.show()

bar_chart(sentiment_count)
    
##############################################################################
################### Step 10: Sentiment Freq. & Pie Chart  ####################
##############################################################################

sentiment_freq = data_set['SentimentClass'].value_counts(normalize=True, sort= True)

#print (sentiment_freq) # Print to check that 

# Set colours for pie chart.  
colors = ['#7EC0EE', '#6CA6CD', '#4A708B']


def pie_chart(sentiment_freq):
    '''
    Objective:
    Function that uses matpotlib (plt) to plot a pie chart of the frequency of
    each sentiment class within the sample of tweets. Set clockwise parameter
    to False and the startangle parameter to 90 to ensure that the first 
    segment of the pie represents the most common class (as the freqs. have 
    been stored in ascending order). Labels have been set to sentiment_freq.index
    to allow them to change accordingly depending on the order. 
    
    Input:
    sentiment_freq = variable holds the freq of each sentiment class in 
    the 'Sentiment Class'  column of 'data_set' calculated using .value_count
    with normalize parameter set to True.  
    
    Output:
    Pie chart diplayed in console and saved in .png format. 
    '''   
    
    plt.pie(sentiment_freq, counterclock=False, labels = sentiment_freq.index, 
        colors = colors, startangle = 90, autopct='%.2f%%', explode = (0.01, 0.01, 0.01))
    if search_by == 'Word':
        '''
        Title of pie chart is dependent on the choice made by user within GUI
        to search by either 'Word' or 'User'. 
        '''
        plt.title("Sentiment Class Frequency of Tweets Containing Search Term "+'"'+query+'"')
    else:
        plt.title("Sentiment Class Frequency of Tweets by "+'"'+query+'"')
    plt.savefig('piechart.png', bbox_inches = 'tight')
    plt.show()

pie_chart(sentiment_freq)

##############################################################################
#################### Step 11: Write Analysis to text file #####################
##############################################################################
 
# Intial test to write to very simple text file.
#f = open('Sentiment_Summary.txt','w') 
#f.write('Tweet Search Summary') 
 
# Added each element to write to text file individually with some additions 
# retuning a blank text file due to issues with format - had to ensure 
# everything was in, or was converted to, string format.  

def write_to_txt():
    '''
    Objectve:
    Function to write details of search and summary of results to text file. 
    
    Inputs:
    query = query term entered by user in GUI 
    language_name = name of language, taken from language dictonary based on 
    639-1 language code entered by user in GUI
    n_tweets_str = number of tweets as entered by user in GUI
    search_datetime = time recorded when search carried out 
    summary.to_string(index = False) = summary data frame converted to string, 
    written to text file without index column. 
    sentiment_count.to_string() = sentiment_count converted to string. 
    entiment_freq.to_string() = sentiment_freq converted to string.  
        
    Output:
    Sentiment_Summary.txt = text file saved to directory 
        
    '''
    f = open('Sentiment_Summary.txt','w') 
 
    f.write('Tweet Sentiment Summary' + '\n' + '' + '\n') 
    if search_by == 'Word':
        '''
        Query label is dependent on the choice made by user within GUI
        to search by either 'Word' or 'User'. 
        '''
        f.write('Search Term: ' + query + '\n')
    else:
        f.write('Username: ' + query + '\n')
    f.write('Language: ' + language_name + '\n')
    f.write('No. of Tweets Requested: ' + n_tweets_str + '' + '\n')
    f.write('No. of Tweets Analysed: ' + tweet_count_str + '' + '\n' )
    f.write('Date & Time of Search: ' + search_datetime + '\n' + '' + '\n')
    f.write('Summary Stats: ' + '\n' + summary.to_string(index = False) + '\n' + '' + '\n')
    f.write('Sentiment Class Count: ' + '\n' + sentiment_count.to_string() + '\n' + '' + '\n') 
    f.write('Sentiment Class Frequency: ' + '\n' + sentiment_freq.to_string() + '\n' + '' + '\n') 
 
    f.close() 

write_to_txt()

# Call 'quit' function to close GUI window once outputs have been produced. 
quit()

##############################################################################
######################## Early Exploration & Learning ########################
##############################################################################

'''
Accessing Twitter Timeline:
    
# By default home_timeline() will return the 20 most recent tweets on the 
# Twitter timeline. Up to 200 tweets can be retieved by setting the 'count' 
# parameter. 
# Store tweets returned in 'timeline_tweets' variable.  
timeline_tweets = api.home_timeline()

# For each tweet within 'timeline_tweets', print the text stored inside
# the tweet object 
for tweet in timeline_tweets:
   print (tweet.text) 
   
   
Accessing Specific User's Timeline:
    
# Assign twitter user to pull tweets from to 'username' variable  
username = "BBCNews"   

# Assign number of tweets to pull to 'tweet_count' variable 
tweet_count = 20 

# Setting parameters within user_timeline function of tweepy and storing 
# returned tweets into 'user_timeline_tweets'
user_timeline_tweets = api.user_timeline(id=username, count=tweet_count)

# For each tweet within 'user_timeline_tweets', print the text, date/time of
# creation, location and username of author stored inside the tweet object. 
for tweet in user_timeline_tweets:
   print (tweet.text)
   print (tweet.created_at) 
   print (tweet.user.location) 
   print (tweet.user.screen_name)


Searching Key Words: 
    
Twitter_Data = [tweet.text, tweet.created_at, tweet.user.location]  
Twitter_File = 'csvexample.csv'

# Assign the search term to 'query' 
query = "Trump"

# Set language of tweets to search for (follows ISO 639-1 language code standards)
# Set to English (en)
language = "en"

# Set parameters of search function to 'query' and 'language' variables
# Store tweets in 'search_tweets' variable 
search_tweets = api.search(q=query, lang=language)

# For each tweet in 'search_tweets', print the text stored within each tweet 
# with associated username and write 'Twitter_Data' to csv file. 

for tweet in results:
   print (tweet.text)
'''