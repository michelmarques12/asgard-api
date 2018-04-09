
from unittest import mock

from hollowman import plugins
from hollowman.app import application
from hollowman.plugins import ASGARD_PLUGIN_LOGGER_REGISTRY

import unittest

class PluginLoaderTest(unittest.TestCase):

    def setUp(self):
        pass

    def test_plugin_load_metrics_plugins(self):
        """
        Plugins do tipo Metric Plugin devem fornecer um objeto do tipo flask.Blueprint.
        Plugins que falharem em fornecer esse objeto não serão carregados

        Aqui temos um plugin, instalado via requirements-dev.txt chamado `asgard-api-plugin-metrics-example-1`
        esse plugin fornece 4 entrypoints. Apenas um dos entrypoints está 100% correto.

        O que esse teste confere é que quando carregamos esse plugin, apenas um novo endpoint é adicionado à
        app flask principal
        """
        logger_mock = mock.MagicMock()
        plugins.load_all_metrics_plugins(application, get_plugin_logger_instance=lambda plugin_id: logger_mock)
        with application.test_client() as client:
            response = client.get("/_cat/metrics/asgard-api-plugin-metrics-example-1/ping")
            self.assertEqual(200, response.status_code)
            self.assertEqual(b"Metrics Plugin Example 1 OK", response.data)
            logger_mock.info.assert_called_with("Log from Mertrics Plugin")
            self.assertTrue(logger_mock is ASGARD_PLUGIN_LOGGER_REGISTRY["asgard-api-plugin-metrics-example-1"])

