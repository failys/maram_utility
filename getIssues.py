#!/usr/bin/python

from requests.auth import HTTPBasicAuth
import json
import requests
import pymongo
import argparse


def addIssuesInPage(r,col,ghUser,ghPasswd):
  issues = r.json()
  for issue in issues:
    iNo = str(issue['number'])
    iState = issue['state']
    iTitle = issue['title']
    iBody = issue['body']
    commentsTxt = []
    cr = requests.get(issue['comments_url'],auth=HTTPBasicAuth(ghUser,ghPasswd))
    if (cr.ok):
      comments = cr.json()
      for comment in comments:
        commentsTxt.append(comment['body'])
    else:
      print 'error getting comments for issue ' + str(iNo) + cr.text
    issueDoc = {"number" : iNo,"state" : iState, "title" : iTitle,"body" : iBody, "comments" : commentsTxt}
    col.insert_one(issueDoc)
    print 'added ' + iState + ' issue ' + issueDoc['number'] 
    

def addIssues(self,ighUser,ighRepo,ghUser,ghPasswd):
  db = conn['maram']
  colName = ighRepo + '_issues'
  issuesCol = db[colName]
  res =issuesCol.delete_many({}).deleted_count
  print 'deleted ' + str(res) + ' documents from ' + colName + ' collection'
  iUrl = 'https://api.github.com/repos/' + ighUser + '/' + ighRepo + '/issues?state=all'
  print 'Retrieving issues from ' + iUrl
  ir = requests.get(iUrl,auth=HTTPBasicAuth(ghUser,ghPasswd))
  if (ir.ok):
    addIssuesInPage(ir,issuesCol,ghUser,ghPasswd)
    last = False
    while (last == False):
      try:
        nextUrl = ir.links['next']['url']
        ir = requests.get(nextUrl,auth=HTTPBasicAuth(credentials[0],credentials[1]))
        if (ir.ok):
          addIssuesInPage(ir,issuesCol,ghUser,ghPasswd)
      except KeyError:
        last = True
  else:
    print 'error getting issues from ' + iUrl + ' : ' + ir.text


if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Retrieve issues from Github repository')
  parser.add_argument('--f',dest='reposFile',help='&&& delimited file of users and repositories')
  parser.add_argument('--ruser',dest='ruser',help='repository user')
  parser.add_argument('--repository',dest='repo',help='repository')
  parser.add_argument('--user',dest='guser',help='github user')
  parser.add_argument('--passwd',dest='gpasswd',help='github password')
  parser.add_argument('--db',dest='dbName',help='mongoDB database name')
  parser.add_argument('--col',dest='dbCol',help='mongoDB collection name')
  args = parser.parse_args() 

  conn = pymongo.MongoClient()

  if (args.reposFile != None):
    with open(args.reposFile) as f:
      repos = f.read().splitlines()
      for repo in repos:
        ghUser,ghRepo = repo.split('&&&')
        addIssues(conn,ghUser,ghRepo,args.guser,args.gpasswd)
  else:
    addIssues(conn,args.ruser,args.repo,args.guser,args.gpasswd)
