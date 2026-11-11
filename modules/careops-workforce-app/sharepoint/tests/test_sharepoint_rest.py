import unittest
from sharepoint_adapter import SharePointRestStore, HttpResponse, Conflict

LISTS={k:'JP_'+k for k in ('heads','operations','artifacts','obligations')}

class SharePointRestTests(unittest.TestCase):
    def test_rest_merges_only_with_exact_etag(self):
        calls=[]
        def send(method,url,headers,body):
            calls.append((method,url,headers,body))
            if method=='GET':return HttpResponse(200,{'value':[{'Id':3,'@odata.etag':'"7"','Payload':'{"generation":1}'}]})
            return HttpResponse(204)
        store=SharePointRestStore(send,LISTS)
        self.assertEqual(store.get('heads','p')[0]['generation'],1)
        store.cas('heads','p','"7"',{'generation':2})
        self.assertEqual(calls[-1][2]['IF-MATCH'],'"7"')
        self.assertEqual(calls[-1][2]['X-HTTP-Method'],'MERGE')
        self.assertEqual(calls[-1][3],{'Payload':'{"generation":2}'})

    def test_rest_412_conflict(self):
        def send(method,url,headers,body):
            if method=='GET':return HttpResponse(200,{'value':[{'Id':3,'@odata.etag':'"7"','Payload':'{}'}]})
            return HttpResponse(412)
        with self.assertRaises(Conflict):
            SharePointRestStore(send,LISTS).cas('heads','p','"7"',{'generation':2})

    def test_unique_key_conflict_requires_exact_key_readback(self):
        def send(method,url,headers,body):
            if method=='POST':return HttpResponse(400)
            return HttpResponse(200,{'value':[{'Id':5,'@odata.etag':'"1"','Payload':'{"a":1}'}]})
        self.assertFalse(SharePointRestStore(send,LISTS).create_unique('operations','X',{'a':1}))

    def test_invalid_list_title_fails(self):
        with self.assertRaises(ValueError):
            SharePointRestStore(lambda *_:None,{**LISTS,'heads':"bad')/Delete"})

if __name__=='__main__':unittest.main()
