from __future__ import absolute_import

import pytest

from detect_secrets.core.constants import VerifiedResult
from detect_secrets.plugins.base import BasePlugin
from testing.factories import potential_secret_factory
from testing.mocks import mock_file_object


def test_fails_if_no_secret_type_defined():
    class MockPlugin(BasePlugin):  # pragma: no cover

        def analyze_string_content(self, *args, **kwargs):
            pass

        def secret_generator(self, *args, **kwargs):
            pass

    with pytest.raises(ValueError) as excinfo:
        MockPlugin()

    assert 'Plugins need to declare a secret_type.' == str(excinfo.value)


class TestVerify:
    @pytest.mark.parametrize(
        'result, output',
        (
            (
                VerifiedResult.UNVERIFIED,
                'True  (unverified)',
            ),
            (
                VerifiedResult.VERIFIED_FALSE,
                'False (verified)',
            ),
            (
                VerifiedResult.VERIFIED_TRUE,
                'True  (verified)',
            ),
        ),
    )
    def test_adhoc_scan_values(self, result, output):
        plugin = self.create_test_plugin(result)
        assert plugin.adhoc_scan('test value') == output

    def test_adhoc_scan_should_abide_by_no_verify_flag(self):
        plugin = self.create_test_plugin(VerifiedResult.VERIFIED_TRUE)
        plugin.should_verify = False

        assert plugin.adhoc_scan('test value') == 'True'

    def test_analyze_verified_false_ignores_value(self):
        plugin = self.create_test_plugin(VerifiedResult.VERIFIED_FALSE)

        file = mock_file_object('does not matter')
        result = plugin.analyze(file, 'does not matter')

        assert len(result) == 0

    def test_analyze_verified_true_adds_intel(self):
        plugin = self.create_test_plugin(VerifiedResult.VERIFIED_TRUE)

        file = mock_file_object('does not matter')
        result = plugin.analyze(file, 'does not matter')

        assert list(result.keys())[0].is_verified

    def test_analyze_unverified_stays_the_same(self):
        plugin = self.create_test_plugin(VerifiedResult.UNVERIFIED)

        file = mock_file_object('does not matter')
        result = plugin.analyze(file, 'does not matter')

        assert not list(result.keys())[0].is_verified

    def test_analyze_should_abide_by_no_verify_flag(self):
        plugin = self.create_test_plugin(VerifiedResult.VERIFIED_FALSE)
        plugin.should_verify = False

        file = mock_file_object('does not matter')
        result = plugin.analyze(file, 'does not matter')

        # If it is verified, this value should be 0.
        assert len(result) == 1

    def create_test_plugin(self, result):
        """
        :type result: VerifiedResult
        """
        class MockPlugin(BasePlugin):  # pragma: no cover
            secret_type = 'test_verify'

            def analyze_string_content(self, *args, **kwargs):
                secret = potential_secret_factory()
                return {
                    secret: secret,
                }

            def secret_generator(self, *args, **kwargs):
                pass

            def verify(self, *args, **kwargs):
                return result

        return MockPlugin()
