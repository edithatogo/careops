from pathlib import Path
import sys
from zipfile import ZipFile
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from ddms_word_namespace_repair import MC, inspect, missing_prefixes, repair


def xml(declaration=''):
    return ('<w:document xmlns:w="urn:w" xmlns:mc="' + MC[1:-1] + '" '
            + declaration + ' mc:Ignorable="w14"><mc:AlternateContent>'
            '<mc:Choice Requires="wpg"><w:p>Human edit</w:p></mc:Choice>'
            '</mc:AlternateContent></w:document>').encode()


def package(path, body):
    with ZipFile(path, 'w') as z:
        z.writestr('word/document.xml', body)
        z.writestr('word/_rels/document.xml.rels', b'unchanged hyperlink relationships')


def test_detects_qname_value_prefixes_despite_well_formed_xml():
    assert missing_prefixes(xml()) == ['w14', 'wpg']
    assert not missing_prefixes(xml('xmlns:w14="urn:14" xmlns:wpg="urn:group"'))


def test_nested_binding_scope_does_not_leak_to_sibling():
    data = ('<r xmlns:mc="' + MC[1:-1] + '"><a xmlns:x="urn:x" mc:Ignorable="x"/>'
            '<b mc:Ignorable="x"/></r>').encode()
    assert missing_prefixes(data) == ['x']


def test_repairs_only_declarations_and_refuses_overwrite(tmp_path):
    source, template, output = [tmp_path / n for n in ('source.docx', 'template.docx', 'output.docx')]
    package(source, xml())
    package(template, xml('xmlns:w14="urn:14" xmlns:wpg="urn:group"'))
    original = source.read_bytes()
    changed = repair(source, template, output)
    assert set(changed) == {'word/document.xml'} and not inspect(output)
    with ZipFile(source) as a, ZipFile(output) as b:
        assert a.namelist() == b.namelist()
        assert a.read('word/_rels/document.xml.rels') == b.read('word/_rels/document.xml.rels')
        fixed = b.read('word/document.xml').replace(b' xmlns:w14="urn:14"', b'').replace(b' xmlns:wpg="urn:group"', b'')
        assert fixed == a.read('word/document.xml')
    with pytest.raises(FileExistsError):
        repair(source, template, output)
    assert source.read_bytes() == original
    with pytest.raises(ValueError, match='separate'):
        repair(source, template, source)


def test_unknown_prefix_refuses_before_output_creation(tmp_path):
    source, template, output = [tmp_path / n for n in ('source.docx', 'template.docx', 'output.docx')]
    package(source, xml())
    package(template, b'<document/>')
    with pytest.raises(ValueError, match='evidence'):
        repair(source, template, output)
    assert not output.exists()


def test_upload_gate_rejects_dropped_mc_alias(tmp_path):
    from docx import Document
    from upload_gate import inspect_docx
    good, bad = tmp_path / 'good.docx', tmp_path / 'bad.docx'
    d = Document(); d.add_paragraph('Human edit'); d.save(good)
    with ZipFile(good) as src, ZipFile(bad, 'w') as dst:
        for entry in src.infolist():
            data = src.read(entry.filename)
            if entry.filename == 'word/document.xml':
                data = data.replace(b'xmlns:w14=', b'xmlns:renamed14=')
            dst.writestr(entry, data)
    assert not inspect_docx(good)
    assert any('Undeclared markup-compatibility' in error for error in inspect_docx(bad))
