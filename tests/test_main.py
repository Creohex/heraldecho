"""Tests for main module."""

from unittest.mock import patch, Mock

import pytest
import requests

from heraldecho import main


class TestSendMessage:
    @patch('heraldecho.main.requests.post')
    @patch('heraldecho.main.p')
    def test_send_message_success(self, mock_print, mock_post):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_post.return_value = mock_response

        main.send_message("http://webhook.test", "Test message", "Test", "test_scheduler")

        mock_post.assert_called_once_with(
            url="http://webhook.test",
            params={},
            json={"content": "Test message"},
            timeout=30
        )
        mock_print.assert_called()

    @patch('heraldecho.main.requests.post')
    @patch('heraldecho.main.p')
    def test_send_message_http_error(self, mock_print, mock_post):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_post.return_value = mock_response

        main.send_message("http://webhook.test", "Test message", "Test", "test_scheduler")

        mock_post.assert_called_once()
        mock_print.assert_called()

    @patch('heraldecho.main.requests.post')
    @patch('heraldecho.main.p')
    def test_send_message_exception(self, mock_print, mock_post):
        mock_post.side_effect = requests.RequestException("Network error")

        main.send_message("http://webhook.test", "Test message", "Test", "test_scheduler")

        mock_post.assert_called_once()
        mock_print.assert_called()

    @patch('heraldecho.main.requests.post')
    @patch('heraldecho.main.p')
    def test_send_message_timeout(self, mock_print, mock_post):
        mock_post.side_effect = requests.Timeout("Request timeout")

        main.send_message("http://webhook.test", "Test message", "Test", "test_scheduler")

        mock_post.assert_called_once()
        mock_print.assert_called()
