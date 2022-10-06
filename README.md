# SearchEngine
GROUP MEMBERS: 
1. AATISH DHAMI     - 027973307
2. ZENIL VAGHASIYA  - 027970577

Description : Built a search engine using positional inverted Index.

Milestone 1
Additional Features(6 points required):
1. Soundex Algorithm - 3points
2. NEAR Operator - 1points
3. WEB UI - 2points (using Flask, Python, HTML, CSS, Bootstrap)

Note: 
Please use webmain.py for WEB GUI and main.py for without GUI
Video for WEB GUI

Instructions

How to run Web App:
-> First run webmain.py instead of main.py
First you need to import Flask 
This will create localhost web server on your machine.
Now you can type below url in your browser to access serach engine web app.
URL : http://127.0.0.1:5000

-> after succesfully running webapp: 
- Enter corpus location of your machine. example : /Users/zenil/IdeaProjects/MobyDick10Chapters
- It will start indexing all dcouments of that directory and displays the elapsed time for indexing.
- Then you will see text box for query. User can add any query such as phrase query("national parks"), single term(national), AND(national park), OR(national + park), or combination of all (fires + "national park" year).
- The application supports following SPECIAL queries:
    1.  :stem token - take the token string and stem it, then print the stemmed term   
    2.  :q - exit the program
    3.  :index directoryname - index the folder specified by directoryname and then begin querying it,effectively restarting the program.
    4.  :vocab - print the first 1000 terms in the vocabulary of the corpus, sorted alphabetically, one term per line. Then prints the count of the total number of vocabulary terms.
- you can view all content of document based on document ID. 


Webapp Sceenshot:

<img width="1728" alt="Search Engine" src="https://user-images.githubusercontent.com/47736398/194021576-8a0f5f3e-7024-4612-b651-f8e9d122282f.png">

