from __future__ import annotations

import asyncio
import logging
from typing import Awaitable, Callable, TypeVar

import openai
from openai import AsyncOpenAI

from .base import LanguageModel

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def _retry_on_error(
    openai_call: Callable[[], Awaitable[T]],
    max_num_trials: int = 5,
    first_wait_time: int = 10,
) -> Awaitable[T] | None:
    for i in range(max_num_trials):
        try:
            # 関数を実行する
            return await openai_call()
        except openai.APIError as e:  # noqa: PERF203
            # 試行回数が上限に達したらエラーを送出
            if i == max_num_trials - 1:
                raise
            logger.info(f"エラーを受け取りました：{e}")
            wait_time_seconds = first_wait_time * (2**i)
            logger.info(f"{wait_time_seconds}秒待機します")
            await asyncio.sleep(wait_time_seconds)
    return None


class OpenAIChatGPT(LanguageModel):
    """
    LanguageModel implementation using OpenAI's ChatGPT API.

    Args:
        model_name: The name of the model to use.
        api_headers: A dictionary of headers to use when making requests to the OpenAI API.
    """

    def __init__(
        self,
        model_name: str = "gpt-3.5-turbo",
        api_headers: dict[str, str] | None = None,
    ) -> None:
        self._model_name = model_name
        if api_headers is None:
            api_headers = {}
        self._client = AsyncOpenAI(**api_headers)

    async def _async_batch_run_chatgpt(
        self,
        messages_list: list[list[dict[str, str]]],
        stop_sequences: str | list[str] | None = None,
        max_new_tokens: int | None = None,
        **kwargs,
    ) -> list[str]:
        """Send multiple chat requests to the OpenAI in parallel."""
        if stop_sequences is not None:
            if "stop" in kwargs:
                msg = (
                    "You specified both `stop_sequences` and `stop` in generation kwargs. "
                    "However, `stop_sequences` will be normalized into `stop`. "
                    "Please specify only one of them."
                )
                raise ValueError(msg)
            kwargs["stop"] = stop_sequences

        if max_new_tokens is not None:
            if "max_tokens" in kwargs:
                msg = (
                    "You specified both `max_new_tokens` and `max_tokens` in generation kwargs. "
                    "However, `max_new_tokens` will be normalized into `max_tokens`. "
                    "Please specify only one of them."
                )
                raise ValueError(msg)
            kwargs["max_tokens"] = max_new_tokens

        tasks = [
            _retry_on_error(
                # Define an anonymous function with a lambda expression and pass it,
                # and call it inside the _retry_on_error function
                openai_call=lambda x=ms: self._client.chat.completions.create(
                    model=self._model_name,
                    messages=x,
                    **kwargs,
                ),
            )
            for ms in messages_list
        ]
        return await asyncio.gather(*tasks)

    def batch_complete_text(
        self,
        text_list: list[str],
        stop_sequences: str | list[str] | None = None,
        max_new_tokens: int | None = None,
        **kwargs,
    ) -> list[str]:
        messages_list = [[{"role": "user", "content": text}] for text in text_list]
        api_responses = asyncio.run(
            self._async_batch_run_chatgpt(
                messages_list,
                stop_sequences=stop_sequences,
                max_new_tokens=max_new_tokens,
                **kwargs,
            ),
        )
        return [res.choices[0].message.content for res in api_responses]

    def batch_generate_chat_response(
        self,
        chat_messages_list: list[list[dict[str, str]]],
        **kwargs,
    ) -> list[str]:
        api_responses = asyncio.run(
            self._async_batch_run_chatgpt(chat_messages_list, **kwargs),
        )
        return [res.choices[0].message.content for res in api_responses]
