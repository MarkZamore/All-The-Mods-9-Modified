from pathlib import Path
import hashlib, importlib.util, json, shutil, subprocess, sys, tempfile, unittest, zipfile

ROOT=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('quiet',ROOT.parent/'grotesque_steve_quiet.py')
quiet=importlib.util.module_from_spec(spec);spec.loader.exec_module(quiet)
AUTHOR=ROOT/'source/grotesque_steve-1.4.2-forge-1.20.1.jar'
OUTPUT=None
_DERIVATIVE_TEMP=None

def setUpModule():
    global OUTPUT, _DERIVATIVE_TEMP
    _DERIVATIVE_TEMP=tempfile.TemporaryDirectory(prefix='grotesque-quiet-test-')
    OUTPUT=Path(_DERIVATIVE_TEMP.name)/'grotesque_steve-1.4.2-quiet.1-forge-1.20.1.jar'
    quiet.build(AUTHOR,OUTPUT)

def tearDownModule():
    if _DERIVATIVE_TEMP is not None:_DERIVATIVE_TEMP.cleanup()


class QuietTests(unittest.TestCase):
    def test_exact_edition_source_unchanged(self):
        self.assertEqual(quiet.digest(AUTHOR.read_bytes()),quiet.AUTHOR_SHA)

    def test_rebuild_bytes_identical_in_different_directory(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'different-name.jar';r=quiet.build(AUTHOR,p)
            self.assertEqual(p.read_bytes(),OUTPUT.read_bytes())
            self.assertEqual(r['outputSha256'],'ffa7df6fb07e54217757436b566fa0073b460c5fa4b695cfd2d4d40692208052')

    def test_only_four_entries_and_no_helper(self):
        with zipfile.ZipFile(AUTHOR) as a,zipfile.ZipFile(OUTPUT) as b:
            self.assertEqual(set(a.namelist()),set(b.namelist()))
            self.assertEqual({n for n in a.namelist() if a.read(n)!=b.read(n)},quiet.CHANGED)

    def test_all_non_callback_methods_byte_identical(self):
        with zipfile.ZipFile(AUTHOR) as a,zipfile.ZipFile(OUTPUT) as b:
            for n in quiet.TARGETS:
                old,new=quiet.ClassFile(a.read(n)),quiet.ClassFile(b.read(n))
                for m,p in zip(old.methods,new.methods):
                    if m['name']!='onPlayerLoggedIn':self.assertEqual(m['raw'],p['raw'])
                    else:
                        self.assertEqual(quiet.code(p)['value'],quiet.QUIET_CODE)
                        self.assertEqual([(x['name'],x['value']) for x in m['attributes'] if x['name']!='Code'],[(x['name'],x['value']) for x in p['attributes'] if x['name']!='Code'])

    def test_book_and_reward_resources_still_available(self):
        with zipfile.ZipFile(AUTHOR) as a,zipfile.ZipFile(OUTPUT) as b:
            for n in a.namelist():
                if 'manual' in n.lower() and n!=quiet.MANUAL or n.endswith('/give.mcfunction') or n.endswith('/grotesque_hello.json'):
                    self.assertEqual(a.read(n),b.read(n),n)
            self.assertEqual(b.read('data/grotesque_steve/functions/give.mcfunction'),b'give @p grotesque_steve:manualbook')

    def test_deterministic_container_metadata(self):
        with zipfile.ZipFile(OUTPUT) as z:
            self.assertEqual(z.namelist(),sorted(z.namelist()))
            for info in z.infolist():
                self.assertEqual(info.create_system,0)
                self.assertEqual(info.date_time,(2026,10,30,0,0,0))
                self.assertEqual(info.compress_type,zipfile.ZIP_STORED)

    def test_wrong_source_hash_refused_without_output(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'modified.jar';blob=bytearray(AUTHOR.read_bytes());blob[-1]^=1;p.write_bytes(blob)
            out=Path(d)/'result.jar'
            with self.assertRaisesRegex(ValueError,'JAR SHA'):quiet.build(p,out)
            self.assertFalse(out.exists())

    def test_wrong_source_size_refused(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'different-edition.jar';p.write_bytes(b'not the user edition')
            with self.assertRaisesRegex(ValueError,'exact user-provided'):quiet.build(p,Path(d)/'out.jar')

    def test_refuse_in_place_author_mutation(self):
        with self.assertRaisesRegex(ValueError,'Separate'):quiet.build(AUTHOR,AUTHOR)
        self.assertEqual(quiet.digest(AUTHOR.read_bytes()),quiet.AUTHOR_SHA)

    def test_stale_class_pin_refused(self):
        with zipfile.ZipFile(AUTHOR) as z:
            name=next(iter(quiet.TARGETS));blob=bytearray(z.read(name));blob[-1]^=1
            with self.assertRaisesRegex(ValueError,'source class SHA'):quiet.patch_class(bytes(blob),name)

    def test_truncated_class_parser_refuses(self):
        with zipfile.ZipFile(AUTHOR) as z:
            blob=z.read(next(iter(quiet.TARGETS)))
            with self.assertRaises(ValueError):quiet.ClassFile(blob[:-1])

    def test_native_metadata_and_manual_exact_delta(self):
        with zipfile.ZipFile(AUTHOR) as a,zipfile.ZipFile(OUTPUT) as b:
            self.assertEqual(b.read(quiet.MANUAL),a.read(quiet.MANUAL)[1:])
            self.assertEqual(b.read(quiet.META),a.read(quiet.META).replace(b'version="1.4.2"',b'version="1.4.2-quiet.1"'))
            self.assertEqual(b.read('pack.mcmeta'),a.read('pack.mcmeta'))

    def test_report_cannot_overwrite_source_or_output(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/'output.jar'
            for report in [AUTHOR,out]:
                result=subprocess.run([sys.executable,'-B',str(ROOT.parent/'grotesque_steve_quiet.py'),'--input',str(AUTHOR),'--output',str(out),'--report',str(report)],capture_output=True)
                self.assertNotEqual(result.returncode,0)
                self.assertIn(b'Report must not alias',result.stderr)
                self.assertFalse(out.exists())
            self.assertEqual(quiet.digest(AUTHOR.read_bytes()),quiet.AUTHOR_SHA)

if __name__=='__main__':unittest.main()
