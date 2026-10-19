from unittest.mock import MagicMock, call

from extras import check_passages


def test_check_known_citation_resolves_and_checks_arxiv_html(monkeypatch):
    target = {"bibcode": "target"}
    citing = {"bibcode": "citing"}
    passages = ["A linked citation passage."]
    resolver_response = MagicMock()
    resolver_response.__enter__.return_value.geturl.return_value = (
        "https://arxiv.org/abs/1234.56789"
    )
    html_response = MagicMock()
    html_response.__enter__.return_value.read.return_value = b"article html"
    open_url = MagicMock(side_effect=[resolver_response, html_response])
    find_passages = MagicMock(return_value=passages)

    monkeypatch.setattr(check_passages, "get_paper", lambda bibcode: target)
    monkeypatch.setattr(check_passages, "urlopen", open_url)
    monkeypatch.setattr(check_passages, "find_citation_passages", find_passages)

    assert check_passages.check_known_citation("target", citing) == (
        citing,
        passages,
    )
    assert open_url.call_args_list == [
        call(
            "https://ui.adsabs.harvard.edu/link_gateway/citing/eprint_html",
            timeout=30,
        ),
        call("https://arxiv.org/html/1234.56789", timeout=30),
    ]
    find_passages.assert_called_once_with("article html", target)
