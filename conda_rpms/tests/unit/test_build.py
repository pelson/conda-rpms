import textwrap
import unittest

from conda_rpms.build import name_version_release


class Test_name_version_release(unittest.TestCase):
    def _check_output(self, spec):
        expected = {'name': 'foo', 'release':'2', 'version':'1'}
        actual = name_version_release(textwrap.dedent(spec).split('\n'))
        self.assertEqual(expected, actual)

    def test_multiple_names(self):
        spec = """
                Name: foo
                Version: 1
                Release: 2
                Name: bar
                """
        self._check_output(spec)

    def test_multiple_versions(self):
        spec = """
                Name: foo
                Version: 1
                Release: 2
                Version: 3
                """
        self._check_output(spec)

    def test_multiple_releases(self):
        spec = """
                Name: foo
                Version: 1
                Release: 2
                Release: 3
                """
        self._check_output(spec)


if __name__ == '__main__':
    unittest.main()
