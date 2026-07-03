from unittest.mock import MagicMock, patch

import pytest

from cli import build_parser, main


def _mock_response(status=200, json_data=None):
    response = MagicMock()
    response.status_code = status
    response.ok = 200 <= status < 300
    response.json.return_value = json_data or []
    return response


@patch("cli._request")
def test_cli_list(mock_request, capsys):
    mock_request.return_value = _mock_response(json_data=[{"id": 1, "product_name": "Tea"}])
    main(["list"])
    out = capsys.readouterr().out
    assert "Tea" in out


@patch("cli._request")
def test_cli_add(mock_request, capsys):
    mock_request.return_value = _mock_response(
        status=201,
        json_data={"id": 4, "product_name": "Juice"},
    )
    main(["add", "Juice", "--price", "3.50", "--stock", "12"])
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert args[0] == "POST"
    assert kwargs["json"]["product_name"] == "Juice"


@patch("cli._request")
def test_cli_update(mock_request):
    mock_request.return_value = _mock_response(json_data={"id": 1, "stock": 99})
    main(["update", "1", "--stock", "99"])
    kwargs = mock_request.call_args.kwargs
    assert kwargs["json"] == {"stock": 99}


@patch("cli._request")
def test_cli_delete(mock_request, capsys):
    mock_request.return_value = _mock_response(status=204)
    main(["delete", "1"])
    assert "Deleted successfully" in capsys.readouterr().out


@patch("cli._request")
def test_cli_find_barcode(mock_request, capsys):
    mock_request.return_value = _mock_response(
        json_data={"status": 1, "product": {"product_name": "Oats"}},
    )
    main(["find-barcode", "030000413004"])
    assert "Oats" in capsys.readouterr().out


def test_parser_requires_command():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args([])
