from mock import call, patch, sentinel
import os
import unittest

import conda_rpms.tests as tests
from conda_rpms.build_rpm_structure import create_rpmbuild_for_env


class Test(tests.CommonTest):
    def setUp(self):
        self.pkgs = [['url1', 'pkg1'],
                     ['url2', 'pkg2']]
        self.prefix = 'Prefix'
        self.config = dict(rpm=dict(prefix=self.prefix))
        self.patch('conda_rpms.install.unlink')

    def test_pkg_all_linked(self):
        func = 'conda_rpms.install.linked'
        with patch(func, return_value=zip(*self.pkgs)[1]):
            with self.temp_dir() as target:
                create_rpmbuild_for_env(self.pkgs, target, self.config)
        spec_dir = os.path.join(target, 'SPECS')
        self.assertFalse(os.path.isdir(spec_dir))

    @patch('conda.fetch.fetch_index', return_value={})
    @patch('conda_rpms.install.linked', return_value=[])
    def test_pkg_unavailable(self, mlinked, mindex):
        with self.temp_dir() as target:
            emsg = 'no longer available in the channel'
            with self.assertRaisesRegexp(ValueError, emsg):
                create_rpmbuild_for_env(self.pkgs, target, self.config)

    @patch('conda_rpms.generate.render_dist_spec', return_value='spec')
    @patch('conda_rpms.install.is_fetched', return_value=True)
    @patch('conda.fetch.fetch_index',
           return_value={'pkg1.tar.bz2': sentinel.pkg1_info,
                         'pkg2.tar.bz2': sentinel.pkg2_info})
    @patch('conda_rpms.install.linked', return_value=[])
    def test_pkg_render(self, mlinked, mindex, mfetched, mrender):
        with self.temp_dir() as target:
            create_rpmbuild_for_env(self.pkgs, target, self.config)
            spec_dir = os.path.join(target, 'SPECS')
            self.assertTrue(os.path.isdir(spec_dir))
            expected = [call(['url1'], use_cache=True),
                        call(['url2'], use_cache=True)]
            self.assertEqual(mindex.call_args_list, expected)
            srcs_dir = os.path.join(target, 'SOURCES')
            expected = [call(srcs_dir, 'pkg1'),
                        call(srcs_dir, 'pkg2')]
            self.assertEqual(mfetched.call_args_list, expected)
            expected = [call(os.path.join(srcs_dir, 'pkg1.tar.bz2'),
                             self.config),
                        call(os.path.join(srcs_dir, 'pkg2.tar.bz2'),
                             self.config)]
            self.assertEqual(mrender.call_args_list, expected)
            fname = '{}-pkg-{}.spec'
            specs = [os.path.join(spec_dir, fname.format(self.prefix, 'pkg1')),
                     os.path.join(spec_dir, fname.format(self.prefix, 'pkg2'))]
            for spec in specs:
                self.assertTrue(os.path.isfile(spec))

    @patch('conda_rpms.generate.render_dist_spec', return_value='spec')
    @patch('conda.fetch.fetch_pkg')
    @patch('conda_rpms.install.is_fetched', return_value=False)
    @patch('conda.fetch.fetch_index',
           return_value={'pkg1.tar.bz2': sentinel.pkg1_info,
                         'pkg2.tar.bz2': sentinel.pkg2_info})
    @patch('conda_rpms.install.linked', return_value=[])
    def test_pkg_fetch_render(self, mlinked, mindex, mfetched, mpkg, mrender):
        with self.temp_dir() as target:
            create_rpmbuild_for_env(self.pkgs, target, self.config)
            spec_dir = os.path.join(target, 'SPECS')
            self.assertTrue(os.path.isdir(spec_dir))
            expected = [call(['url1'], use_cache=True),
                        call(['url2'], use_cache=True)]
            self.assertEqual(mindex.call_args_list, expected)
            srcs_dir = os.path.join(target, 'SOURCES')
            expected = [call(srcs_dir, 'pkg1'),
                        call(srcs_dir, 'pkg2')]
            self.assertEqual(mfetched.call_args_list, expected)
            expected = [call(sentinel.pkg1_info, srcs_dir),
                        call(sentinel.pkg2_info, srcs_dir)]
            self.assertEqual(mpkg.call_args_list, expected)
            expected = [call(os.path.join(srcs_dir, 'pkg1.tar.bz2'),
                             self.config),
                        call(os.path.join(srcs_dir, 'pkg2.tar.bz2'),
                             self.config)]
            self.assertEqual(mrender.call_args_list, expected)
            fname = '{}-pkg-{}.spec'
            specs = [os.path.join(spec_dir, fname.format(self.prefix, 'pkg1')),
                     os.path.join(spec_dir, fname.format(self.prefix, 'pkg2'))]
            for spec in specs:
                self.assertTrue(os.path.isfile(spec))


if __name__ == '__main__':
    unittest.main()
