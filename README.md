# What is this?

This is a small Python script that scans an mbox email archive and tries to figure out which domains you likely have accounts on.
It scores emails based on subject keywords (like welcome, verify, reset) and filters out newsletters and common noise. It also has an ignore list where you would probably want to add domains like your university emails

Basically: “Which websites did I probably sign up for?”

# How to use it

- Get your email archive (.pst), plenty of resources online on how to do this
- Convert the .pst to mbox
- Rename your email archive MBOX file to "mb"
- Edit these text files to your liking and place in the same directory of the python file:
  - account_keywords.txt
  - newsletter_keywords.txt
  - ignore_domains.txt
-  Run:
  python parse.py (probably need to pip install tldextract)

TO DO:
1. RAG + MCP thing
2. Try ML classification (again)
3. Maybe read the body of the email for classification
