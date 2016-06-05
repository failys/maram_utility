#!/usr/bin/python

from requests.auth import HTTPBasicAuth
import json
import requests
import pymongo
import argparse


def addIssues(r,col):
  issues = r.json()
  for issue in issues:
    iNo = str(issue['number'])
    iState = issue['state']
    iTitle = issue['title']
    iBody = issue['body']
    commentsTxt = []
    cr = requests.get(issue['comments_url'],auth=HTTPBasicAuth(credentials[0],credentials[1]))
    if (cr.ok):
      comments = cr.json()
      for comment in comments:
        commentsTxt.append(comment['body'])
    else:
      print 'error getting comments for issue ' + str(iNo) + cr.text
    issueDoc = {"number" : iNo,"state" : iState, "title" : iTitle,"body" : iBody, "comments" : commentsTxt}
    issuesCol.insert_one(issueDoc)
    print 'added ' + iState + ' issue ' + issueDoc['number'] 
    

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Retrieve issues from Github repository')
  parser.add_argument('--ruser',dest='ruser',help='repository user')
  parser.add_argument('--repository',dest='repo',help='repository')
  parser.add_argument('--user',dest='guser',help='github user')
  parser.add_argument('--passwd',dest='gpasswd',help='github password')
  parser.add_argument('--db',dest='dbName',help='mongoDB database name')
  parser.add_argument('--col',dest='dbCol',help='mongoDB collection name')
  args = parser.parse_args() 

  conn = pymongo.MongoClient()
  db = conn[args.dbName]
  issuesCol = db[args.dbCol]
  res =issuesCol.delete_many({}).deleted_count
  print 'deleted ' + str(res) + ' documents from ' + args.dbCol + ' collection'

  iUrl = 'https://api.github.com/repos/' + args.ruser + '/' + args.repo + '/issues?state=all'
  credentials = (args.guser,args.gpasswd)
  ir = requests.get(iUrl,auth=HTTPBasicAuth(credentials[0],credentials[1]))
  if (ir.ok):
    addIssues(ir,issuesCol)
    last = False
    while (last == False):
      try:
        nextUrl = ir.links['next']['url']
        ir = requests.get(nextUrl,auth=HTTPBasicAuth(credentials[0],credentials[1]))
        if (ir.ok):
          addIssues(ir,issuesCol)
      except KeyError:
        last = True
  else:
    print 'error getting issues: ' + ir.text
