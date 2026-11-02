import hashlib
import unittest
try:
    from scripts.ppg_external_reconciliation import group_pdf_uri_occurrences, pdf_uri_inspection, reference_scope, representation_scope
except ModuleNotFoundError as error:
    if error.name != 'bs4':
        raise
    raise unittest.SkipTest('Optional catalogue HTML profile missing; use the qualified hash-locked Python 3.15.1 profile') from error


class ReferenceScopeTests(unittest.TestCase):
    def setup_case(self):
        text='NSQHS Standards second edition unknown. '+('Fictional retained text. '*8)
        original=b'fictional original'; raw=text.encode()
        s=dict(documentUID='fictional',originalSHA256=hashlib.sha256(original).hexdigest(),textSHA256=hashlib.sha256(raw).hexdigest(),text=text,originalPath='original',textPath='text',extractionError=None,identityState='exact_register_identifier',sourceVersion='retained',versionConflict=True)
        p=dict(kind='Publication',key='acsqhc:nsqhs',assertions=[])
        return s,p,{'original':original,'text':raw}

    def test_literal_match_preserves_conflict_and_does_not_choose_latest_edition(self):
        s,p,files=self.setup_case();r=reference_scope([{'DocumentUID':'fictional'}],[s],[p],read_bytes=files.__getitem__)
        self.assertEqual(r['occurrenceCount'],1);o=r['occurrences'][0]
        self.assertEqual(o['literal'],'NSQHS Standards');self.assertEqual(o['resolution'],'publication-only')
        self.assertIsNone(o['editionKey']);self.assertTrue(o['versionConflict'])
        self.assertFalse(r['completeExternalReferenceCoverage']);self.assertEqual(r['nativeWrites'],0)
        self.assertEqual(r,reference_scope([{'DocumentUID':'fictional'}],[s],[p],read_bytes=files.__getitem__))

    def test_hash_mismatch_is_held_and_unsearched_identity_accounted(self):
        s,p,files=self.setup_case();files['text']+=b'edited'
        r=reference_scope([{'DocumentUID':'fictional'},{'DocumentUID':'missing'}],[s],[p],read_bytes=files.__getitem__)
        self.assertEqual(r['occurrenceCount'],0);self.assertEqual(len(r['heldSources']),1)
        self.assertEqual(r['sourceStates'],{'some-retained-text-held':1,'no-retained-source':1})

    def capsule_case(self, *, member_bytes=None, duplicate=False):
        from io import BytesIO
        from zipfile import ZipFile
        s,p,files=self.setup_case();out=BytesIO()
        with ZipFile(out,'w') as archive:
            archive.writestr('historical.doc', files['original'] if member_bytes is None else member_bytes)
            if duplicate:
                with self.assertWarns(UserWarning):
                    archive.writestr('historical.doc',files['original'])
        files['capsule']=out.getvalue()
        s.update(identityState='verified_source_identity',appliesToRequestedEdition=False,
                 originalCapsule={'path':'capsule','sha256':hashlib.sha256(files['capsule']).hexdigest(),'member':'historical.doc'})
        return s,p,files

    def test_verified_historical_capsule_retains_identity_without_adopting_edition(self):
        s,p,files=self.capsule_case()
        r=reference_scope([{'DocumentUID':'fictional'}],[s],[p],read_bytes=files.__getitem__)
        self.assertEqual(r['occurrenceCount'],1);o=r['occurrences'][0]
        self.assertEqual(o['sourceIdentityState'],'verified_source_identity')
        self.assertEqual(o['originalCapsuleSHA256'],s['originalCapsule']['sha256'])
        self.assertEqual(o['originalCapsuleMember'],'historical.doc')
        self.assertEqual(o['resolution'],'publication-only');self.assertIsNone(o['editionKey'])
        self.assertTrue(o['versionConflict']);self.assertFalse(o['clinicalApplicabilityAccepted'])
        self.assertEqual(r['nativeWrites'],0);self.assertFalse(r['completeExternalReferenceCoverage'])

    def test_capsule_provenance_does_not_leak_to_following_plain_source(self):
        capsule,p,files=self.capsule_case()
        plain,_,_=self.setup_case();plain['documentUID']='plain'
        r=reference_scope([{'DocumentUID':'fictional'},{'DocumentUID':'plain'}],
                          [capsule,plain],[p],read_bytes=files.__getitem__)
        self.assertEqual(r['occurrenceCount'],2)
        self.assertIn('originalCapsuleSHA256',r['occurrences'][0])
        for field in ('sourceIdentityState','originalCapsuleSHA256','originalCapsuleMember'):
            self.assertNotIn(field,r['occurrences'][1])

    def test_corrupt_compressed_member_is_held_and_next_source_is_inspected(self):
        from io import BytesIO
        from zipfile import ZIP_DEFLATED, ZipFile
        s,p,files=self.capsule_case();out=BytesIO()
        with ZipFile(out,'w',compression=ZIP_DEFLATED) as archive:
            archive.writestr('historical.doc',files['original'])
        raw=bytearray(out.getvalue())
        data_start=30+int.from_bytes(raw[26:28],'little')+int.from_bytes(raw[28:30],'little')
        raw[data_start]=7  # Reserved DEFLATE block type, with intact ZIP headers.
        files['capsule']=bytes(raw)
        s['originalCapsule']['sha256']=hashlib.sha256(files['capsule']).hexdigest()
        plain,_,_=self.setup_case();plain['documentUID']='plain'
        r=reference_scope([{'DocumentUID':'fictional'},{'DocumentUID':'plain'}],
                          [s,plain],[p],read_bytes=files.__getitem__)
        self.assertEqual(r['heldSources'][0]['reason'],'original_capsule_binding_unqualified')
        self.assertEqual(r['occurrenceCount'],1)
        self.assertEqual(r['occurrences'][0]['documentUID'],'plain')

    def test_unbound_or_ambiguous_original_capsules_stay_held(self):
        import copy
        valid=self.capsule_case()
        variants=[]
        for field,value in [('sha256','0'*64),('sha256',1),('member','missing.doc'),('path','missing')]:
            s,p,files=copy.deepcopy(valid);s['originalCapsule'][field]=value;variants.append((s,p,files))
        s,p,files=copy.deepcopy(valid);del s['originalCapsule'];variants.append((s,p,files))
        variants.extend([self.capsule_case(member_bytes=b'another original'),self.capsule_case(duplicate=True)])
        s,p,files=copy.deepcopy(valid);files['capsule']=b'not a ZIP';s['originalCapsule']['sha256']=hashlib.sha256(files['capsule']).hexdigest();variants.append((s,p,files))
        for s,p,files in variants:
            with self.subTest(capsule=s.get('originalCapsule')):
                r=reference_scope([{'DocumentUID':'fictional'}],[s],[p],read_bytes=files.__getitem__)
                self.assertEqual(r['occurrenceCount'],0)
                self.assertEqual(r['heldSources'][0]['reason'],'original_capsule_binding_unqualified')

    def test_capsule_proof_does_not_bypass_text_or_identity_holds(self):
        s,p,files=self.capsule_case();files['text']+=b'changed'
        r=reference_scope([{'DocumentUID':'fictional'}],[s],[p],read_bytes=files.__getitem__)
        self.assertEqual(r['heldSources'][0]['reason'],'original_or_text_hash_binding_differs')
        s,p,files=self.capsule_case();s['identityState']='unreviewed'
        r=reference_scope([{'DocumentUID':'fictional'}],[s],[p],read_bytes=files.__getitem__)
        self.assertEqual(r['occurrenceCount'],0);self.assertEqual(r['heldSources'][0]['reason'],'identity_association_unqualified')

    def test_duplicate_identity_or_source_refuses(self):
        s,p,files=self.setup_case()
        for cat,sources in [([{'DocumentUID':'fictional'}]*2,[s]),([{'DocumentUID':'fictional'}],[s,s])]:
            with self.assertRaises(ValueError):reference_scope(cat,sources,[p],read_bytes=files.__getitem__)

    def test_same_url_ambiguous_publications_stay_ambiguous(self):
        s,p,files=self.setup_case();url='https://www.safetyandquality.gov.au/resources/fictional'
        s['text']=url+' '+('fictional '*20);files['text']=s['text'].encode();s['textSHA256']=hashlib.sha256(files['text']).hexdigest()
        pubs=[dict(kind='Publication',key=k,assertions=[{'sourceURL':url}]) for k in ['first','second']]
        r=reference_scope([{'DocumentUID':'fictional'}],[s],pubs,read_bytes=files.__getitem__)
        self.assertEqual(r['resolutionCounts'],{'ambiguous':1});self.assertEqual(r['occurrences'][0]['candidatePublicationKeys'],['first','second'])

    def test_selected_publisher_urls_exclude_names_and_other_origins(self):
        s,p,files=self.setup_case()
        url='https://publisher.example.org/fictional/guideline.pdf'
        s['text']='NSQHS Standards '+url+' '+url+' https://intranet.example.org/local.pdf https://publisher.example.org.evil.test/x https://publisher.example.org:invalid/x https://user@publisher.example.org/x '+('fictional '*20)
        files['text']=s['text'].encode();s['textSHA256']=hashlib.sha256(files['text']).hexdigest()
        pubs=[dict(kind='Publication',key='qh:fictional',assertions=[{'sourceURL':url}])]
        options=dict(read_bytes=files.__getitem__,publisher_hosts=['publisher.example.org'],include_nsqhs_names=False)
        r=reference_scope([{'DocumentUID':'fictional'}],[s],pubs,**options)
        self.assertEqual(r['occurrenceCount'],2)
        self.assertEqual(len({x['key'] for x in r['occurrences']}),2)
        self.assertEqual(r['resolutionCounts'],{'publication-only':2})
        self.assertTrue(all(x['editionKey'] is None and x['versionConflict'] for x in r['occurrences']))
        self.assertFalse(r['completeExternalReferenceCoverage'])
        files['text']+=b'changed'
        self.assertEqual(reference_scope([{'DocumentUID':'fictional'}],[s],pubs,**options)['occurrenceCount'],0)

    def test_balanced_url_parentheses_and_citation_punctuation(self):
        s,p,files=self.setup_case();url='https://publisher.example.org/guideline(2026)'
        s['text']=url+' '+url+'). '+('fictional '*20)
        files['text']=s['text'].encode();s['textSHA256']=hashlib.sha256(files['text']).hexdigest()
        pubs=[dict(kind='Publication',key='pub',assertions=[{'sourceURL':url}])]
        r=reference_scope([{'DocumentUID':'fictional'}],[s],pubs,read_bytes=files.__getitem__,publisher_hosts=['publisher.example.org'],include_nsqhs_names=False)
        self.assertEqual(r['resolutionCounts'],{'publication-only':2})
        self.assertTrue(all(x['candidatePublicationKeys']==['pub'] for x in r['occurrences']))

    def test_unqualified_reference_host_and_flag_refused(self):
        s,p,files=self.setup_case()
        for hosts,flag in [([],False),(['evil.test/path'],False),(['publisher.example.org'],1)]:
            with self.assertRaises(ValueError):
                reference_scope([{'DocumentUID':'fictional'}],[s],[p],read_bytes=files.__getitem__,publisher_hosts=hosts,include_nsqhs_names=flag)

    def test_representation_page_absence_never_becomes_complete(self):
        r=representation_scope({'records':[dict(kind='Publication',key='fictional',requiredCapture=True)]},'.')
        self.assertEqual(len(r['pageGaps']),1);self.assertFalse(r['requiredRepresentationDenominatorDeclared'])


    def test_representation_links_preserve_occurrences_and_missing_captures(self):
        import tempfile
        from pathlib import Path
        raw=b'<main><h1>Fictional</h1><a href="/one.pdf">One</a><a href="/one.pdf">Again</a></main>'
        with tempfile.TemporaryDirectory() as temp:
            Path(temp,'page.html').write_bytes(raw)
            pub=dict(kind='Publication',key='pub',requiredCapture=True)
            page=dict(kind='Capture',key='page',publicationKey='pub',editionKey=None,data=dict(mimeType='text/html',file='page.html',sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),sourceURL='https://www.safetyandquality.gov.au/resources/fictional'))
            r=representation_scope({'records':[pub,page]},temp)
            self.assertEqual(r['candidateOccurrences'],2);self.assertEqual(r['uniquePublicationURLs'],1)
            self.assertEqual(r['notRetainedOccurrences'],2)
            Path(temp,'page.html').write_bytes(raw+b'edit')
            with self.assertRaises(ValueError):representation_scope({'records':[pub,page]},temp)

    def test_malformed_representation_link_does_not_discard_valid_candidates(self):
        import tempfile
        from pathlib import Path
        raw=b'<main><a href="https://www.safetyandquality.gov.au:invalid/bad.pdf">Bad port</a><a href="https://[broken/file.pdf">Bad bracket</a><a href="/valid.pdf">Valid</a></main>'
        with tempfile.TemporaryDirectory() as temp:
            Path(temp,'page.html').write_bytes(raw)
            pub=dict(kind='Publication',key='pub',requiredCapture=True)
            page=dict(kind='Capture',key='page',publicationKey='pub',editionKey=None,data=dict(mimeType='text/html',file='page.html',sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),sourceURL='https://www.safetyandquality.gov.au/resources/fictional'))
            r=representation_scope({'records':[pub,page]},temp)
            self.assertEqual(r['candidateOccurrences'],1)
            self.assertEqual(len(r['malformedLinks']),2)
            self.assertTrue(all(x['reason']=='malformed_link_authority' for x in r['malformedLinks']))
            self.assertFalse(r['requiredRepresentationDenominatorDeclared'])

    def test_exact_retained_capture_url_identifies_publication_not_cited_edition(self):
        s,p,files=self.setup_case();url='https://publisher.example.org/original.pdf'
        s['text']=url+' '+('fictional '*20);files['text']=s['text'].encode();s['textSHA256']=hashlib.sha256(files['text']).hexdigest()
        records=[dict(kind='Publication',key='pub',assertions=[]),dict(kind='Capture',key='capture:one',publicationKey='pub',editionKey='edition:one',assertions=[],data={'sourceURL':url})]
        r=reference_scope([{'DocumentUID':'fictional'}],[s],records,read_bytes=files.__getitem__,publisher_hosts=['publisher.example.org'],include_nsqhs_names=False)
        o=r['occurrences'][0];self.assertEqual(o['candidatePublicationKeys'],['pub'])
        self.assertEqual(o['urlMatchRecordKeys'],['capture:one']);self.assertEqual(o['resolution'],'publication-only')
        self.assertIsNone(o['editionKey']);self.assertTrue(o['versionConflict'])
        r=reference_scope([{'DocumentUID':'fictional'}],[s],records[1:],read_bytes=files.__getitem__,publisher_hosts=['publisher.example.org'],include_nsqhs_names=False)
        self.assertEqual(r['resolutionCounts'],{'unresolved':1})

    def test_pdf_uri_inspection_preserves_pages_duplicates_and_encoded_targets(self):
        dump='Page  Type          URL\n   2  Annotation    https://publisher.example.org/one.pdf\n   2  Annotation    https://publisher.example.org/one.pdf\n   4  Annotation    https://www.google.com/url?url=https%3A%2F%2Fpublisher.example.org%2Ftwo.pdf\n'
        q=pdf_uri_inspection(dump,'1'*64,decode_url_wrappers=True)
        self.assertEqual(len(q['entries']),3)
        self.assertEqual(q['entries'][2]['decodedTarget'],'https://publisher.example.org/two.pdf')
        self.assertEqual(q['text'].split('\f')[1].count('https://publisher.example.org/one.pdf'),2)
        self.assertIn('Encoded URL target',q['text'].split('\f')[3])
        self.assertEqual(q['retrievals'],0);self.assertFalse(q['fullTextReview'])
        self.assertFalse(pdf_uri_inspection(dump,'1'*64)['entries'][2]['decodedTarget'])
        self.assertEqual(q['annotationOutputSHA256'],hashlib.sha256(dump.encode()).hexdigest())

    def test_pdf_uri_inspection_refuses_bad_dump_and_records_bad_uris(self):
        for dump in ['wrong header','Page Type URL\n0 Annotation https://publisher.example.org/x','Page Type URL\n1 Unknown https://publisher.example.org/x']:
            with self.assertRaises(ValueError):pdf_uri_inspection(dump,'1'*64)
        q=pdf_uri_inspection('Page Type URL\n1 Annotation mailto:fictional@example.org\n1 Annotation https://publisher.example.org:invalid/x\n1 Annotation https://publisher.example.org/space here','1'*64)
        self.assertEqual(len(q['ignoredURIs']),3);self.assertEqual(q['entries'],[])
        with self.assertRaises(ValueError):pdf_uri_inspection('Page Type URL','bad')

    def test_pdf_annotation_reference_scope_retains_representation_provenance(self):
        s,p,files=self.setup_case();dump='Page Type URL\n3 Annotation https://publisher.example.org/guideline.pdf'
        q=pdf_uri_inspection(dump,s['originalSHA256'])
        s.update(text=q['text'],textSHA256=q['textSHA256'],inspectionKind=q['inspectionKind'],annotationOutputSHA256=q['annotationOutputSHA256'])
        files['text']=q['text'].encode()
        r=reference_scope([{'DocumentUID':'fictional'}],[s],[],read_bytes=files.__getitem__,publisher_hosts=['publisher.example.org'],include_nsqhs_names=False)
        self.assertEqual(r['occurrenceCount'],1);o=r['occurrences'][0]
        self.assertEqual(o['page'],3);self.assertEqual(o['inspectionKind'],'pdf-uri-annotations')
        self.assertEqual(o['annotationOutputSHA256'],q['annotationOutputSHA256'])
        self.assertEqual(o['method'],'literal-PDF-URI-annotation');self.assertEqual(o['resolution'],'unresolved')

    def test_explicit_annotation_uri_is_not_trimmed_as_prose(self):
        s,p,files=self.setup_case();base='https://publisher.example.org/guideline'
        for suffix in ['.',';',')']:
            q=pdf_uri_inspection('Page Type URL\n1 Annotation '+base+suffix,s['originalSHA256'])
            s.update(text=q['text'],textSHA256=q['textSHA256'],inspectionKind=q['inspectionKind'],annotationOutputSHA256=q['annotationOutputSHA256']);files['text']=q['text'].encode()
            records=[dict(kind='Publication',key='pub',assertions=[{'sourceURL':base}])]
            r=reference_scope([{'DocumentUID':'fictional'}],[s],records,read_bytes=files.__getitem__,publisher_hosts=['publisher.example.org'],include_nsqhs_names=False)
            self.assertEqual(r['resolutionCounts'],{'unresolved':1})
            self.assertEqual(r['occurrences'][0]['literal'],base+suffix)
            self.assertEqual(r['occurrences'][0]['urlMatchRecordKeys'],[])
        empty=pdf_uri_inspection('Page Type URL','1'*64)
        invalid=pdf_uri_inspection('Page Type URL\n1 Annotation mailto:fictional@example.org','1'*64)
        self.assertEqual(empty['text'],invalid['text']);self.assertFalse(empty['text'].endswith('\n'))

    def test_annotation_grouping_preserves_every_physical_location(self):
        s,p,files=self.setup_case();q=pdf_uri_inspection('Page Type URL\n1 Annotation https://publisher.example.org/x\n2 Annotation https://publisher.example.org/x',s['originalSHA256'])
        s.update(text=q['text'],textSHA256=q['textSHA256'],inspectionKind=q['inspectionKind'],annotationOutputSHA256=q['annotationOutputSHA256']);files['text']=q['text'].encode()
        r=reference_scope([{'DocumentUID':'fictional'}],[s],[],read_bytes=files.__getitem__,publisher_hosts=['publisher.example.org'],include_nsqhs_names=False)
        grouped=group_pdf_uri_occurrences(r)
        self.assertEqual(grouped['occurrenceCount'],1);self.assertEqual(grouped['annotationOccurrenceCount'],2)
        self.assertEqual({x['key'] for x in grouped['occurrences'][0]['annotationOccurrences']},{x['key'] for x in r['occurrences']})
        self.assertEqual([x['page'] for x in grouped['occurrences'][0]['annotationOccurrences']],[1,2])
        import copy
        bad=copy.deepcopy(r);bad['occurrences'][1]['versionConflict']=False
        with self.assertRaises(ValueError):group_pdf_uri_occurrences(bad)
        bad=copy.deepcopy(r);bad['occurrenceCount']=3
        with self.assertRaises(ValueError):group_pdf_uri_occurrences(bad)

    def link_xml(self):
        return b'''<?xml version="1.0"?><!DOCTYPE pdf2xml SYSTEM "pdf2xml.dtd">
<pdf2xml><page number="13">
<text top="10" left="20" width="50" height="8"><a href="https://publisher.example.org/x">Medication </a></text>
<text top="20" left="20" width="50" height="8"><a href="https://publisher.example.org/x">Administration</a></text>
<text top="20" left="100" width="20" height="8">Unrelated column</text>
<text top="30" left="20" width="50" height="8"><a href="mailto:fictional@example.org">Contact</a></text>
</page></pdf2xml>'''

    def test_link_labels_preserve_fragments_positions_and_duplicate_targets(self):
        from scripts.ppg_external_reconciliation import pdf_link_label_inspection
        raw=self.link_xml();r=pdf_link_label_inspection(raw,'1'*64)
        self.assertEqual([x['label'] for x in r['entries']],['Medication ','Administration'])
        self.assertEqual([x['textBox']['top'] for x in r['entries']],[10,20])
        self.assertEqual(r['ignoredLinks'][0]['label'],'Contact')
        self.assertEqual(r['xmlSHA256'],hashlib.sha256(raw).hexdigest())
        self.assertFalse(r['originalBindingVerified']);self.assertFalse(r['fullTextReview'])
        self.assertFalse(r['editionVerified']);self.assertEqual(r['nativeWrites'],0)

    def test_link_xml_rejects_entities_malformed_boxes_and_duplicate_pages(self):
        from scripts.ppg_external_reconciliation import pdf_link_label_inspection
        raw=self.link_xml()
        variants=[b'<broken',b'<wrong/>',raw.decode().encode('utf-16'),raw.replace(b'top="10"',b'top="nan"'),
                  raw.replace(b'number="13"',b'number="0"'),
                  raw.replace(b'</pdf2xml>',b'<page number="13"/></pdf2xml>'),
                  raw.replace(b'<pdf2xml>',b'<!DOCTYPE x [<!ENTITY x "content">]><pdf2xml>')]
        for value in variants:
            with self.subTest(value=value[:50]),self.assertRaises(ValueError):
                pdf_link_label_inspection(value,'1'*64)
        for value in [None,'not bytes']:
            with self.assertRaises(ValueError):pdf_link_label_inspection(value,'1'*64)

    def test_link_label_cli_uses_private_frozen_copy_and_create_only_output(self):
        import tempfile,contextlib,io
        from pathlib import Path
        from unittest.mock import patch,MagicMock
        from scripts.ppg_external_reconciliation import pdf_link_labels_main
        raw=b'%PDF-1.4 fictional source';seen=[]
        with tempfile.TemporaryDirectory() as temp:
            original=Path(temp)/'original.pdf';original.write_bytes(raw);out=Path(temp)/'links.json'
            args=['--original',str(original),'--original-sha256',hashlib.sha256(raw).hexdigest(),
                  '--page','13','--output',str(out)]
            def popen(command,**kwargs):
                frozen=Path(command[-1]);seen.append(frozen)
                self.assertNotEqual(frozen,original);self.assertEqual(frozen.read_bytes(),raw)
                self.assertEqual(frozen.stat().st_mode&0o777,0o600)
                self.assertIn('-i',command)
                process=MagicMock();process.__enter__.return_value=process
                process.stdout=io.BytesIO(self.link_xml());process.wait.return_value=0
                process.poll.return_value=0
                return process
            with patch('shutil.which',return_value='/fictional/pdftohtml'),patch('subprocess.Popen',side_effect=popen),contextlib.redirect_stdout(io.StringIO()):
                pdf_link_labels_main(args)
                with self.assertRaises(ValueError):pdf_link_labels_main(args)
            import json
            r=json.loads(out.read_text());self.assertTrue(r['originalBindingVerified'])
            self.assertEqual(r['selectedPage'],13);self.assertEqual(out.stat().st_mode&0o777,0o600)
            self.assertEqual(original.read_bytes(),raw);self.assertFalse(seen[0].exists())

    def test_link_label_cli_refuses_unselected_empty_page(self):
        import tempfile,contextlib,io
        from pathlib import Path
        from unittest.mock import patch,MagicMock
        from scripts.ppg_external_reconciliation import pdf_link_labels_main
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'source.pdf';raw=b'%PDF-1.4 fictional';p.write_bytes(raw)
            out=Path(temp)/'out.json'
            def popen(command,**kwargs):
                process=MagicMock();process.__enter__.return_value=process
                process.stdout=io.BytesIO(b'<pdf2xml><page number="14"/></pdf2xml>')
                process.wait.return_value=0;process.poll.return_value=0
                return process
            with patch('shutil.which',return_value='/fictional/pdftohtml'),patch('subprocess.Popen',side_effect=popen),contextlib.redirect_stdout(io.StringIO()):
                with self.assertRaises(ValueError):pdf_link_labels_main([
                    '--original',str(p),'--original-sha256',hashlib.sha256(raw).hexdigest(),
                    '--page','13','--output',str(out)])
            self.assertFalse(out.exists())

    def test_link_cli_stops_oversize_output_and_rejects_processor_failure(self):
        import tempfile,contextlib,io
        from pathlib import Path
        from unittest.mock import patch,MagicMock
        from scripts.ppg_external_reconciliation import pdf_link_labels_main
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/'source.pdf';raw=b'%PDF-1.4 fictional';p.write_bytes(raw)
            for data,status,running in [(b'x'*(8*1024*1024+1),0,True),(self.link_xml(),2,False)]:
                process=MagicMock();process.__enter__.return_value=process
                process.stdout=io.BytesIO(data);process.wait.return_value=status
                process.poll.return_value=None if running else status
                out=Path(temp)/'out.json'
                with patch('shutil.which',return_value='/fictional/pdftohtml'),patch('subprocess.Popen',return_value=process),contextlib.redirect_stdout(io.StringIO()):
                    with self.assertRaises(ValueError):pdf_link_labels_main([
                        '--original',str(p),'--original-sha256',hashlib.sha256(raw).hexdigest(),
                        '--page','13','--output',str(out)])
                self.assertFalse(out.exists())
                if running:process.kill.assert_called_once()

    def test_cli_capsule_read_stays_within_source_root(self):
        import tempfile,json,contextlib,io
        from pathlib import Path
        from scripts.ppg_external_reconciliation import main
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);approved=root/'approved';approved.mkdir()
            s,p,files=self.capsule_case()
            (approved/'original').write_bytes(files['original']);(approved/'text').write_bytes(files['text'])
            (root/'capsule').write_bytes(files['capsule'])
            s.update(originalPath=str(approved/'original'),textPath=str(approved/'text'))
            s['originalCapsule']['path']=str(root/'capsule')
            (root/'bundle.json').write_text(json.dumps({'records':[dict(p,requiredCapture=False)]}))
            (root/'local.json').write_text(json.dumps({'catalogue':[{'DocumentUID':'fictional'}],'sources':[s]}))
            args=['--bundle',str(root/'bundle.json'),'--local-inputs',str(root/'local.json'),
                  '--capture-root',str(root),'--source-root',str(approved),'--output-dir',str(root/'out')]
            with contextlib.redirect_stdout(io.StringIO()):main(args)
            selected=json.loads((root/'out/references.json').read_text())
            self.assertEqual(selected['occurrenceCount'],0)
            self.assertEqual(selected['heldSources'][0]['reason'],'original_capsule_binding_unqualified')
            self.assertEqual(selected['nativeWrites'],0)

    def test_cli_manifest_is_create_only_and_binds_inputs(self):
        import tempfile,json,contextlib,io
        from pathlib import Path
        from scripts.ppg_external_reconciliation import main
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);s,p,files=self.setup_case()
            for name,raw in files.items():Path(root,name).write_bytes(raw)
            s['originalPath']=str(root/'original');s['textPath']=str(root/'text')
            (root/'bundle.json').write_text(json.dumps({'records':[dict(p,requiredCapture=False)]}))
            (root/'local.json').write_text(json.dumps({'catalogue':[{'DocumentUID':'fictional'}],'sources':[s]}))
            args=['--bundle',str(root/'bundle.json'),'--local-inputs',str(root/'local.json'),'--capture-root',temp,'--source-root',temp,'--output-dir',str(root/'out'),'--publisher-host','publisher.example.org','--no-nsqhs-names']
            with contextlib.redirect_stdout(io.StringIO()):main(args)
            manifest=json.loads((root/'out/manifest.json').read_text())
            self.assertEqual(manifest['nativeWrites'],0)
            selected=json.loads((root/'out/references.json').read_text())
            self.assertEqual(selected['publisherHosts'],['publisher.example.org'])
            self.assertFalse(selected['includeNSQHSNames'])
            self.assertEqual(selected['occurrenceCount'],0)
            self.assertEqual(manifest['outputs']['references.json'],hashlib.sha256((root/'out/references.json').read_bytes()).hexdigest())
            self.assertEqual((root/'out/references.json').stat().st_mode&0o777,0o600)
            with self.assertRaises(ValueError):main(args)


if __name__=='__main__':unittest.main()
