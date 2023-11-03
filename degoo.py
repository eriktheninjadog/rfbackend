import base64
import pathlib
import requests

import json

import hashlib
import sys
import getopt
import argparse

def build_graph_request(operation,accesstoken,querystring):
    data = {}
    data["operationName"]=operation
    data["variables"]={"Token":accesstoken}
    data["query"] = querystring    
    return data

url = 'https://rest-api.degoo.com/login'
data = '{"Username":"erik.tamm@eriktamm.com","Password":"ninjadogs","GenerateToken":true}'
response = requests.post(url, data=data)
print(response.headers)

resp = response.json()
print(resp['RefreshToken'])

# I need to provide X-API-Authnenti
#ykTNlZTMhZ2YzkDMtUjZwgTL5cDN00CM0cTZtYGN4EDM4UDO

#now lets go for the v2 whidch I am not sure why we need but there is an accessotken there
data = {}
data['RefreshToken'] = resp['RefreshToken']
url = 'https://rest-api.degoo.com/access-token/v2'   
headers = {}
headers['X-Amz-Content']='degoo.com/CgQyMTQy'
headers['X-Api-Authentication']='ykTNlZTMhZ2YzkDMtUjZwgTL5cDN00CM0cTZtYGN4EDM4UDO'
headers['X-Api-Key']= "da2-vs6twz5vnjdavpqndtbzg3prra"
response = requests.post(url, headers = headers,data=json.dumps(data))
print(response.json())
accesstoken = response.json()['AccessToken']

# get files
url = 'https://production-appsync.degoo.com/graphql'
data = '{"operationName":"GetFileChildren5","variables":{"Token":"'+accesstoken+'","ParentID":"0","Limit":50,"Order":1},"query":"query GetFileChildren5(\n    $Token: String!\n    $ParentID: String\n    $AllParentIDs: [String]\n    $Limit: Int!\n    $Order: Int!\n    $NextToken: String\n  ) {\n    getFileChildren5(\n      Token: $Token\n      ParentID: $ParentID\n      AllParentIDs: $AllParentIDs\n      Limit: $Limit\n      Order: $Order\n      NextToken: $NextToken\n    ) {\n      Items {\n        ID\n        MetadataID\n        UserID\n        DeviceID\n        MetadataKey\n        Name\n        FilePath\n        LocalPath\n        LastUploadTime\n        LastModificationTime\n        ParentID\n        Category\n        Size\n        Platform\n        URL\n        ThumbnailURL\n        CreationTime\n        IsSelfLiked\n        Likes\n        IsHidden\n        IsInRecycleBin\n        Description\n        Location2 {\n          Country\n          Province\n          Place\n          GeoLocation {\n            Latitude\n            Longitude\n          }\n        }\n        Data\n        DataBlock\n        CompressionParameters\n        Shareinfo {\n          Status\n          ShareTime\n        }\n        ShareInfo {\n          Status\n          ShareTime\n        }\n        Distance\n        OptimizedURL\n        Country\n        Province\n        Place\n        GeoLocation {\n          Latitude\n          Longitude\n        }\n        Location\n        IsShared\n        ShareTime\n      }\n      NextToken\n    }\n  }"}'
#print(data)
data = {}
data["operationName"]="GetUserInfo3"
data["variables"]={"Token":accesstoken}

query = """query GetUserInfo3($Token: String!) {
    getUserInfo3(Token: $Token) {
      ID
      FirstName
      LastName
      Email
      AvatarURL
      CountryCode
      LanguageCode
      Phone
      AccountType
      UsedQuota
      TotalQuota
      OAuth2Provider
      GPMigrationStatus
      FeatureNoAds
      FeatureTopSecret
      FeatureDownsampling
      FeatureAutomaticVideoUploads
      FileSizeLimit
    }
  }"""

data = build_graph_request("GetUserInfo3",accesstoken, query)
response = requests.post(url, headers = headers,data=json.dumps(data))
print(response.json())

query = """query GetFileChildren5(
    $Token: String!
    $ParentID: String
    $AllParentIDs: [String]
    $Limit: Int!
    $Order: Int!
    $NextToken: String
  ) {
    getFileChildren5(
      Token: $Token
      ParentID: $ParentID
      AllParentIDs: $AllParentIDs
      Limit: $Limit
      Order: $Order
      NextToken: $NextToken
    ) {
      Items {
        ID
        MetadataID
        UserID
        DeviceID
        MetadataKey
        Name
        FilePath
        LocalPath
        LastUploadTime
        LastModificationTime
        ParentID
        Category
        Size
        Platform
        URL
        ThumbnailURL
        CreationTime
        IsSelfLiked
        Likes
        IsHidden
        IsInRecycleBin
        Description
        Location2 {
          Country
          Province
          Place
          GeoLocation {
            Latitude
            Longitude
          }
        }
        Data
        DataBlock
        CompressionParameters
        Shareinfo {
          Status
          ShareTime
        }
        ShareInfo {
          Status
          ShareTime
        }
        Distance
        OptimizedURL
        Country
        Province
        Place
        GeoLocation {
          Latitude
          Longitude
        }
        Location
        IsShared
        ShareTime
      }
      NextToken
    }
  }
"""

# so far soo good

                            
data = build_graph_request("GetFileChildren5",accesstoken, query)
data["variables"]['Limit'] = 100
data["variables"]['Order'] = 3
data["variables"]['ParentID'] = "-1"

response = requests.post(url, headers = headers,data=json.dumps(data))
print(response.json())



def check_sum(filename, blocksize=65536):
    Seed = bytes([13, 7, 2, 2, 15, 40, 75, 117, 13, 10, 19, 16, 29, 23, 3, \
36])
    Hash = hashlib.sha1(Seed)
    with open(filename, "rb") as f:
        for block in iter(lambda: f.read(blocksize), b""):
            Hash.update(block)

        cs = list(bytearray(Hash.digest()))
        #                                                                       
        # TODO: Can we move this from an hypothesis to a conclusion?            
        #CS = [10, len(cs)] + cs + [16, 0]
        CS = [10, len(cs)] + cs + [16, 0]

        # Finally, Degoo base64 encode is cehcksum.                             
        checksum = base64.urlsafe_b64encode(bytes(CS)).decode()
        #org = base64.b64decode("ChSpYlC3twbjiPu4pBBMb7vYKYpG2RAC")
        # the one I calculate  'ChRKWJOWwbwrD1M+E2j0fOiFv4CGVRAA'
        #org = base64.b64decode("ChRKWJOWwbwrD1M-E2j0fOiFv4CGVRAA")
        org = base64.urlsafe_b64decode("ChRKWJOWwbwrD1M-E2j0fOiFv4CGVRAA")
        


        orgb = list(bytearray(org))
        print(str(CS))
        print(str(orgb))
        return  checksum



def upload_file(filepath,accesstoken,parentid="19960708431"):
    query = """query GetBucketWriteAuth4(
        $Token: String!
        $ParentID: String!
        $StorageUploadInfos: [StorageUploadInfo2]
    ) {
        getBucketWriteAuth4(
        Token: $Token
        ParentID: $ParentID
        StorageUploadInfos: $StorageUploadInfos
        ) {
        AuthData {
            PolicyBase64
            Signature
            BaseURL
            KeyPrefix
            AccessKey {
            Key
            Value
            }
            ACL
            AdditionalBody {
            Key
            Value
            }
        }
        Error
        }
    }"""

    checksum =  "ChSpYlC3twbjiPu4pBBMb7vYKYpG2RAC"
    print(str(len(checksum)))
    filelength = 0
    with open(filepath, 'rb') as f:
        # Read the entire file into memory
        data = f.read()
        filelength = len(data)
    checksum = check_sum(filepath)
    print(checksum)
        

    data = build_graph_request("GetBucketWriteAuth4",accesstoken, query)
    data["variables"]['ParentID'] = parentid
    data["variables"]['StorageUploadInfos'] = {"Checksum":checksum,"FileName":filepath,"Size":""+str(filelength)+""}
    response = requests.post(url, headers = headers,data=json.dumps(data))
    print(response.json())
    data = response.json()
    policybase = data['data']['getBucketWriteAuth4'][0]['AuthData']['PolicyBase64']
    print(policybase)
    baseurl = data['data']['getBucketWriteAuth4'][0]['AuthData']['BaseURL']
    print(baseurl)
    keyprefix = data['data']['getBucketWriteAuth4'][0]['AuthData']['KeyPrefix']
    print(keyprefix)
    #the key for the post form is keyprefix+"/txt/"+checksum+".txt"
    signature = data['data']['getBucketWriteAuth4'][0]['AuthData']['Signature']
    print(signature)
    #https://s3.wasabisys.com/degoo-production-large-file-us-east1.degoo.info/
    #


    extension = pathlib.Path(filepath).suffix
    extension = extension.replace('.','')


    awsaccesskeyname = data['data']['getBucketWriteAuth4'][0]['AuthData']['AccessKey']['Key']
    awsaccesskeyvalue = data['data']['getBucketWriteAuth4'][0]['AuthData']['AccessKey']['Value']
    files = {
#        'key': (None, keyprefix+"txt/"+checksum+".txt"),
         'key': (None, keyprefix+extension+"/"+checksum+"."+extension),

        'acl':(None,'private'),
        'policy':(None,policybase),
        'signature':(None,signature),
        awsaccesskeyname:(None,awsaccesskeyvalue),
        'Cache-control': (None,'Cache-Control: public, max-age=8674000'),
        'Content-Type':(None,'text/plain'),
        'file':( filepath,open(filepath,"r",),'text/plain'),
    }
    response = requests.post(baseurl, files=files, timeout=30)
    print(response.text)
    print(response.status_code)

    #set it
    query ="""mutation SetUploadFile3($Token: String!, $FileInfos: [FileInfoUpload3]!) {
                setUploadFile3(Token: $Token, FileInfos: $FileInfos)
                    }"""
    data = build_graph_request("SetUploadFile3",accesstoken, query)
    data["variables"]['FileInfos'] = {"ParentID":"19960708431", "Checksum":checksum,"Size":str(filelength),"Name":filepath,"CreationTime":"1697174980329"}
    response = requests.post(url, headers = headers,data=json.dumps(data))
    print(response.text)
    print(response.status_code)



def listfiles(accesstoken,parentid = "0"):
    query = query = """query GetFileChildren5(
    $Token: String!
    $ParentID: String
    $AllParentIDs: [String]
    $Limit: Int!
    $Order: Int!
    $NextToken: String
  ) {
    getFileChildren5(
      Token: $Token
      ParentID: $ParentID
      AllParentIDs: $AllParentIDs
      Limit: $Limit
      Order: $Order
      NextToken: $NextToken
    ) {
      Items {
        ID
        MetadataID
        UserID
        DeviceID
        MetadataKey
        Name
        FilePath
        LocalPath
        LastUploadTime
        LastModificationTime
        ParentID
        Category
        Size
        Platform
        URL
        ThumbnailURL
        CreationTime
        IsSelfLiked
        Likes
        IsHidden
        IsInRecycleBin
        Description
        Location2 {
          Country
          Province
          Place
          GeoLocation {
            Latitude
            Longitude
          }
        }
        Data
        DataBlock
        CompressionParameters
        Shareinfo {
          Status
          ShareTime
        }
        ShareInfo {
          Status
          ShareTime
        }
        Distance
        OptimizedURL
        Country
        Province
        Place
        GeoLocation {
          Latitude
          Longitude
        }
        Location
        IsShared
        ShareTime
      }
      NextToken
    }
  }
"""
    data = build_graph_request("GetFileChildren5",accesstoken, query)
    data["variables"]['Limit'] = 100
    data["variables"]['Order'] = 1
    data["variables"]['ParentID'] = parentid
    response = requests.post(url, headers = headers,data=json.dumps(data))
    ret = response.json()
    items = ret['data']['getFileChildren5']['Items']
    for i in items:
        print(i['Name'] + " " + i["ID"] + " " + str(i["Category"]))



def download_file(fileid,filename,accesstoken):
    query = """query GetOverlay4($Token: String!, $ID: IDType!) {
    getOverlay4(Token: $Token, ID: $ID) {
      ID
      MetadataID
      UserID
      DeviceID
      MetadataKey
      Name
      FilePath
      LocalPath
      LastUploadTime
      LastModificationTime
      ParentID
      Category
      Size
      Platform
      URL
      ThumbnailURL
      CreationTime
      IsSelfLiked
      Likes
      Comments
      IsHidden
      IsInRecycleBin
      Description
      Location {
        Country
        Province
        Place
        GeoLocation {
          Latitude
          Longitude
        }
      }
      Location2 {
        Country
        Region
        SubRegion
        Municipality
        Neighborhood
        GeoLocation {
          Latitude
          Longitude
        }
      }
      Data
      DataBlock
      CompressionParameters
      Shareinfo {
        Status
        ShareTime
      }
      ShareInfo {
        Status
        ShareTime
      }
      HasViewed
      QualityScore
    }
  }"""
    data = build_graph_request("GetOverlay4",accesstoken, query)
    data["variables"]['ID'] = {"FileID":fileid}
    response = requests.post(url, headers = headers,data=json.dumps(data))
    ret = response.json()
    theurl = ret['data']['getOverlay4']['URL']
    data = {}
    data['URLs'] = [theurl]
    repsonse2 = requests.post("https://rest-api.degoo.com/url-to-cf", data= json.dumps(data), timeout=30)
    rawurl = repsonse2.json()[0]
    rawurl = rawurl + "&response-content-disposition=attachment;%20filename=%22poe.py%22&ngsw-bypass=1"
    response3 = requests.get(rawurl)
    with open(filename,"wb") as f:
        f.write(response3.content)
    print("done")

#listfiles(accesstoken)
#download_file("19963163303","anotherbeat.txt",accesstoken)
#upload_file('main.py',accesstoken)
#https://degoo-production-large-file-us-east1.degoo.info/AEIu64/zIy7Eg/py/ChTFvCLuxtcBJO-oGWjBkaaWNKLcqRAA.py?AWSAccessKeyId=QCIW8NA9JUUC4PKQYZTJ&Expires=1699536223&Signature=1C2K8Xhx3BqnbuBKM6101uf5AVE%3D&response-content-disposition=attachment;%20filename=%22poe.py%22&ngsw-bypass=1






if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Degoo command')
    parser.add_argument('--parentid','-p',help='parent id, assumed to be default if not')
    parser.add_argument('--id','-i',help='file id, assumed to be "0"" if not')

    parser.add_argument('--filename','-f',help='filename, assumed to be "text.txt" if not')
    parser.add_argument('--command','-c',help='command, assumed to be list if not')

    args = parser.parse_args()
    parentid = "0"
    command = "list"
    fileid = "0"
    if args.parentid:
        parentid = args.parentid
    else:
        parentid = "0"

    if args.command:
        command = args.command
    
    if args.filename:
        filename = args.filename
    else:
        filename = "text.txt"

    if args.id:
        fileid = args.id
    else:
        fileid = "0"
   

    if command == "put":
        upload_file(filename,accesstoken,parentid=parentid)
    if command == "get":
        download_file(fileid,filename,accesstoken)
    if command == "list":
        listfiles(accesstoken,parentid=parentid)
