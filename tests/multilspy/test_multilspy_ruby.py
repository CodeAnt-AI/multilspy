"""
This file contains tests for running the Ruby Language Server: solargraph
"""

import unittest
import pytest

from multilspy import LanguageServer
from multilspy.multilspy_config import Language
from multilspy.multilspy_types import Position, CompletionItemKind
from tests.test_utils import create_test_context
from pathlib import PurePath
from tests.multilspy.test_sync_multilspy_ruby import EXPECTED_RESULT


@pytest.mark.asyncio
async def test_multilspy_ruby_rubyland():
    """
    Test the working of multilspy with ruby repository - rubyland
    """
    code_language = Language.RUBY
    params = {
        "code_language": code_language,
        "repo_url": "https://github.com/jrochkind/rubyland/",
        "repo_commit": "c243ee2533a5822f5699a2475e492927ace039c7"
    }
    with create_test_context(params) as context:
        lsp = LanguageServer.create(context.config, context.logger, context.source_directory)

        # All the communication with the language server must be performed inside the context manager
        # The server process is started when the context manager is entered and is terminated when the context manager is exited.
        # The context manager is an asynchronous context manager, so it must be used with async with.
        async with lsp.start_server():
            result = await lsp.request_definition(str(PurePath("app/controllers/feed_controller.rb")), 11, 23)

            assert isinstance(result, list)
            assert len(result) == 2
            item = result[1]
            assert item["relativePath"] == str(PurePath("app/models/feed.rb"))
            assert item["range"] == {
                "start": {"line": 0, "character": 0},
                "end": {"line": 42, "character": 3},
            }

            result = await lsp.request_references(str(PurePath("app/models/feed.rb")), 0, 7)

            assert isinstance(result, list)
            assert len(result) == 8

            for item in result:
                del item["uri"]
                del item["absolutePath"]

            case = unittest.TestCase()
            case.assertCountEqual(
                result,
                EXPECTED_RESULT,
            )
