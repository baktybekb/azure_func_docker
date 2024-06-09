# test_function.py
import unittest
from unittest.mock import patch, MagicMock
import logging
from io import StringIO

from my_function import main


class TestFunction(unittest.TestCase):

    @patch('my_function.settings')
    @patch('azure.functions.TimerRequest')
    def test_main(self, mock_timer_request, mock_settings):
        # Mock settings
        mock_settings.api_key = 'fake_api_key'

        # Mock TimerRequest
        mock_timer_request_instance = MagicMock()
        mock_timer_request.return_value = mock_timer_request_instance

        # Redirect logging output
        log_stream = StringIO()
        logging.basicConfig(stream=log_stream, level=logging.INFO)

        # Call the function
        main(mock_timer_request_instance)

        # Retrieve log output
        log_contents = log_stream.getvalue()

        # Assertions
        self.assertIn("API Key: fake_api_key", log_contents)
        self.assertIn("Buuhaaaaaaaaaaaaaaaaaaaaaaa", log_contents)
        self.assertIn("Docker image deployment version", log_contents)


if __name__ == '__main__':
    unittest.main()
