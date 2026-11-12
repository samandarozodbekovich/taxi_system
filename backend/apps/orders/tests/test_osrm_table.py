from unittest import mock

from django.test import SimpleTestCase

from services import get_table_to


def mock_response(payload, status_code=200):
    response = mock.Mock(status_code=status_code)
    response.json.return_value = payload
    return response


class OsrmTableTests(SimpleTestCase):
    """Parsing the OSRM table response (no network, requests.get is mocked)."""

    def test_one_request_for_all_drivers(self):
        payload = {"code": "Ok", "durations": [[120.0], [None], [600.0]], "distances": [[1500.0], [None], [8000.0]]}
        with mock.patch("requests.get", return_value=mock_response(payload)) as get:
            result = get_table_to([(41.30, 69.20), (41.31, 69.21), (41.32, 69.22)], 41.29, 69.19)

        get.assert_called_once()
        self.assertEqual(get.call_args.kwargs["params"]["destinations"], "3")
        self.assertEqual(result, [
            {"duration_minutes": 2.0, "distance_km": 1.5},
            None,  # no route found
            {"duration_minutes": 10.0, "distance_km": 8.0},
        ])

    def test_server_error_returns_none(self):
        with mock.patch("requests.get", return_value=mock_response({}, 503)):
            self.assertIsNone(get_table_to([(41.3, 69.2)], 41.29, 69.19))

    def test_no_sources_makes_no_request(self):
        with mock.patch("requests.get") as get:
            self.assertEqual(get_table_to([], 41.29, 69.19), [])
        get.assert_not_called()
