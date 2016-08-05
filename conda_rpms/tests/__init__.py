import contextlib
import shutil
import tempfile
import unittest

import mock


class CommonTest(unittest.TestCase):
    """
    A sub-class of :class:`unittest.TestCase` that provides common
    testing functionality.

    """
    def _remove_testcase_patches(self):
        """Helper to remove per-testcase patches installed by :meth:`patch`."""
        # Remove all patches made, ignoring errors.
        for p in self.testcase_patches:
            p.stop()
        # Reset per-test patch control variable.
        self.testcase_patches.clear()

    def patch(self, *args, **kwargs):
        """
        Install a mock.patch, to be removed after the current test.

        The patch is created with mock.patch(*args, **kwargs).

        Returns:
            The substitute object returned by patch.start().

        For example::

            mock_call = self.patch('module.Class.call', return_value=1)
            module_Class_instance.call(3, 4)
            self.assertEqual(mock_call.call_args_list, [mock.call(3, 4)])

        """
        # Make the new patch and start it.
        patch = mock.patch(*args, **kwargs)
        start_result = patch.start()

        # Create the per-testcases control variable if it does not exist.
        # NOTE: this mimics a setUp method, but continues to work when a
        # subclass defines its own setUp.
        if not hasattr(self, 'testcase_patches'):
            self.testcase_patches = {}

        # When installing the first patch, schedule remove-all at cleanup.
        if not self.testcase_patches:
            self.addCleanup(self._remove_testcase_patches)

        # Record the new patch and start object for reference.
        self.testcase_patches[patch] = start_result

        # Return patch replacement object.
        return start_result

    @contextlib.contextmanager
    def temp_dir(self, suffix='', prefix='tmp', dir=None):
        dname = tempfile.mkdtemp(suffix=suffix,
                                 prefix=prefix,
                                 dir=dir)
        try:
            yield dname
        finally:
            shutil.rmtree(dname) 
