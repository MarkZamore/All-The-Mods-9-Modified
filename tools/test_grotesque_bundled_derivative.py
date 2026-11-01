"""Local supplied-edition provenance and exact derivative restore, without URLs."""
from pathlib import Path
import base64,copy,hashlib,io,unittest,zipfile
from unittest.mock import patch
import restore_modified as restore
import verify_modified as verify
import test_modified_tools as fixtures


def jar(version):
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w') as z:
        z.writestr('META-INF/mods.toml',f'modLoader="javafml"\nloaderVersion="[47,)"\nlicense="MIT"\n[[mods]]\nmodId="grotesque_steve"\nversion="{version}"\n')
    return stream.getvalue()


class BundledDerivativeTests(unittest.TestCase):
    def setUp(self):
        f=fixtures.ModifiedCompositionTests('test_exact_composition_passes_without_claiming_runtime');f.setUp();self.addCleanup(f.doCleanups)
        self.f=f;self.pack=f.pack;self.cache=f.cache;self.original=jar('1.4.2');self.new=jar('1.4.2-quiet.1')
        self.approved=copy.deepcopy(verify.APPROVED_GROTESQUE_QUIET)
        self.approved.update(originalSha256=hashlib.sha256(self.original).hexdigest(),originalSizeBytes=len(self.original),sha256=hashlib.sha256(self.new).hexdigest(),sizeBytes=len(self.new))
        source=self.pack/self.approved['originalPath'];source.parent.mkdir(parents=True);source.write_bytes(self.original)
        self.write_tool(self.new)
        patcher=patch.object(verify,'APPROVED_GROTESQUE_QUIET',self.approved);patcher.start();self.addCleanup(patcher.stop)
        row=f.bundled_row();row.update({k:self.approved[k] for k in ['path','fileName','sha256','sizeBytes','version']});row['modIds']=['grotesque_steve']
        row['transformation']={'kind':'grotesque-steve-quiet',**{k:self.approved[k] for k in ['patchTool','patchToolSha256','originalPath','originalSha256','originalSizeBytes']},'reason':'Explicit quiet-login and native function syntax correction'}
        self.row=row;f.lock['files']=[row];f.addon.unlink();f.save_lock()

    def write_tool(self,output):
        tool=self.pack/self.approved['patchTool'];tool.parent.mkdir(parents=True,exist_ok=True)
        tool.write_text('import argparse,base64\nfrom pathlib import Path\np=argparse.ArgumentParser();p.add_argument("--input");p.add_argument("--output");a=p.parse_args();Path(a.output).write_bytes(base64.b64decode('+repr(base64.b64encode(output).decode())+'))\n',encoding='utf-8')
        self.approved['patchToolSha256']=hashlib.sha256(tool.read_bytes()).hexdigest()

    def bytes(self):return {p.relative_to(self.pack):p.read_bytes() for p in self.pack.rglob('*') if p.is_file()}

    def reject_before_normalize(self):
        before=self.bytes()
        with patch.object(restore,'urlopen') as network,patch.object(restore,'run_quest_localization') as normalize:
            with self.assertRaises(ValueError):restore.restore(self.pack,self.cache)
        network.assert_not_called();normalize.assert_not_called();self.assertEqual(before,self.bytes())

    def test_missing_derivative_is_rebuilt_locally_and_second_restore_is_exact(self):
        with patch.object(restore,'urlopen',side_effect=AssertionError('Bundled source is never downloaded')):
            a=restore.restore(self.pack,self.cache);b=restore.restore(self.pack,self.cache)
        self.assertEqual((self.pack/self.row['path']).read_bytes(),self.new)
        self.assertEqual((self.pack/self.approved['originalPath']).read_bytes(),self.original)
        self.assertEqual(a['jarFiles'],2);self.assertEqual(b['restoredAdditionalJars'],0)
        self.assertEqual(a['downloadedAdditionalJars'],0)

    def test_missing_original_source_fails_before_base_or_network(self):
        (self.pack/self.approved['originalPath']).unlink();self.reject_before_normalize()

    def test_changed_tool_or_unknown_existing_derivative_is_not_overwritten(self):
        (self.pack/self.approved['patchTool']).write_bytes(b'changed tool');self.reject_before_normalize()

    def test_unknown_existing_derivative_target_fails_prewrite(self):
        (self.pack/self.row['path']).write_bytes(b'unknown user JAR');self.reject_before_normalize()

    def test_other_edition_or_mod_cannot_borrow_this_transformation(self):
        self.row['modIds']=['another_mod'];self.f.save_lock();self.reject_before_normalize()

    def test_no_download_source_or_arbitrary_tool_path_is_accepted(self):
        self.row['sourceUrl']='https://example.invalid/other-edition.jar';self.f.save_lock();self.reject_before_normalize()
        del self.row['sourceUrl'];self.row['transformation']['patchTool']='tools/another.py';self.f.save_lock();self.reject_before_normalize()

    def test_bad_derivative_bytes_fail_before_any_base_normalization(self):
        self.write_tool(b'bad derivative');self.row['transformation']['patchToolSha256']=self.approved['patchToolSha256'];self.f.save_lock()
        self.reject_before_normalize()


if __name__=='__main__':unittest.main(verbosity=2)
