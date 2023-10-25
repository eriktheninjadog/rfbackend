


from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field
from typing_extensions import Literal, TypeAlias

import sys

Identifier: TypeAlias = str
FeedbackType: TypeAlias = Literal["like", "dislike"]
ContentType: TypeAlias = Literal["text/markdown", "text/plain"]
ErrorType: TypeAlias = Literal["user_message_too_long"]


class MessageFeedback(BaseModel):
    """Feedback for a message as used in the Poe protocol."""

    type: FeedbackType
    reason: Optional[str]


class Attachment(BaseModel):
    url: str
    content_type: str
    name: str


class ProtocolMessage(BaseModel):
    """A message as used in the Poe protocol."""

    role: Literal["system", "user", "bot"]
    content: str
    content_type: ContentType = "text/markdown"
    timestamp: int = 0
    message_id: str = ""
    feedback: List[MessageFeedback] = Field(default_factory=list)
    attachments: List[Attachment] = Field(default_factory=list)


class BaseRequest(BaseModel):
    """Common data for all requests."""

    version: str
    type: Literal["query", "settings", "report_feedback", "report_error"]


class QueryRequest(BaseRequest):
    """Request parameters for a query request."""

    query: List[ProtocolMessage]
    user_id: Identifier
    conversation_id: Identifier
    message_id: Identifier
    metadata: Identifier = ""
    api_key: str = "<missing>"
    access_key: str = "<missing>"
    temperature: float = 0.7
    skip_system_prompt: bool = False
    logit_bias: Dict[str, float] = {}
    stop_sequences: List[str] = []


class SettingsRequest(BaseRequest):
    """Request parameters for a settings request."""


class ReportFeedbackRequest(BaseRequest):
    """Request parameters for a report_feedback request."""

    message_id: Identifier
    user_id: Identifier
    conversation_id: Identifier
    feedback_type: FeedbackType


class ReportErrorRequest(BaseRequest):
    """Request parameters for a report_error request."""

    message: str
    metadata: Dict[str, Any]


class SettingsResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    context_clear_window_secs: Optional[int] = None  # deprecated
    allow_user_context_clear: bool = True  # deprecated
    server_bot_dependencies: Dict[str, int] = Field(default_factory=dict)
    allow_attachments: bool = False
    introduction_message: str = ""


class PartialResponse(BaseModel):
    """Representation of a (possibly partial) response from a bot."""

    # These objects are usually instantiated in user code, so we
    # disallow extra fields to prevent mistakes.
    model_config = ConfigDict(extra="forbid")

    text: str
    """Partial response text.

    If the final bot response is "ABC", you may see a sequence
    of PartialResponse objects like PartialResponse(text="A"),
    PartialResponse(text="B"), PartialResponse(text="C").

    """

    raw_response: object = None
    """For debugging, the raw response from the bot."""

    full_prompt: Optional[str] = None
    """For debugging, contains the full prompt as sent to the bot."""

    request_id: Optional[str] = None
    """May be set to an internal identifier for the request."""

    is_suggested_reply: bool = False
    """If true, this is a suggested reply."""

    is_replace_response: bool = False
    """If true, this text should completely replace the previous bot text."""


class ErrorResponse(PartialResponse):
    """Communicate errors from server bots."""

    allow_retry: bool = False
    error_type: Optional[ErrorType] = None


class MetaResponse(PartialResponse):
    """Communicate 'meta' events from server bots."""

    linkify: bool = True
    suggested_replies: bool = True
    content_type: ContentType = "text/markdown"
    refetch_settings: bool = False


"""

Client for talking to other Poe bots through the Poe bot query API.
For more details, see: https://developer.poe.com/server-bots/accessing-other-bots-on-poe

"""

class BotMessage(PartialResponse):
    None

import asyncio
import contextlib
import json
import warnings
from dataclasses import dataclass, field
from typing import Any, AsyncGenerator, Callable, Dict, List, Optional, cast

import httpx
import httpx_sse


PROTOCOL_VERSION = "1.0"
MESSAGE_LENGTH_LIMIT = 10_000

IDENTIFIER_LENGTH = 32
MAX_EVENT_COUNT = 1000

ErrorHandler = Callable[[Exception, str], None]


class BotError(Exception):
    """Raised when there is an error communicating with the bot."""


class BotErrorNoRetry(BotError):
    """Subclass of BotError raised when we're not allowed to retry."""


class InvalidBotSettings(Exception):
    """Raised when a bot returns invalid settings."""


def _safe_ellipsis(obj: object, limit: int) -> str:
    if not isinstance(obj, str):
        obj = repr(obj)
    if len(obj) > limit:
        obj = obj[: limit - 3] + "..."
    return obj


@dataclass
class _BotContext:
    endpoint: str
    session: httpx.AsyncClient = field(repr=False)
    api_key: Optional[str] = field(default=None, repr=False)
    on_error: Optional[ErrorHandler] = field(default=None, repr=False)

    @property
    def headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.api_key is not None:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    async def report_error(
        self, message: str, metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Report an error to the bot server."""
        if self.on_error is not None:
            long_message = (
                f"Protocol bot error: {message} with metadata {metadata} "
                f"for endpoint {self.endpoint}"
            )
            self.on_error(BotError(message), long_message)
        await self.session.post(
            self.endpoint,
            headers=self.headers,
            json={
                "version": PROTOCOL_VERSION,
                "type": "report_error",
                "message": message,
                "metadata": metadata or {},
            },
        )

    async def report_feedback(
        self,
        message_id: Identifier,
        user_id: Identifier,
        conversation_id: Identifier,
        feedback_type: str,
    ) -> None:
        """Report message feedback to the bot server."""
        await self.session.post(
            self.endpoint,
            headers=self.headers,
            json={
                "version": PROTOCOL_VERSION,
                "type": "report_feedback",
                "message_id": message_id,
                "user_id": user_id,
                "conversation_id": conversation_id,
                "feedback_type": feedback_type,
            },
        )

    async def fetch_settings(self) -> SettingsResponse:
        """Fetches settings from a Poe server bot endpoint."""
        resp = await self.session.post(
            self.endpoint,
            headers=self.headers,
            json={"version": PROTOCOL_VERSION, "type": "settings"},
        )
        return resp.json()

    async def perform_query_request(
        self, request: QueryRequest
    ) -> AsyncGenerator[PartialResponse, None]:
        chunks: List[str] = []
        message_id = request.message_id
        event_count = 0
        error_reported = False
        async with httpx_sse.aconnect_sse(
            self.session,
            "POST",
            self.endpoint,
            headers=self.headers,
            json=request.dict(),
        ) as event_source:
            async for event in event_source.aiter_sse():
                event_count += 1
                if event.event == "done":
                    # Don't send a report if we already told the bot about some other mistake.
                    if not chunks and not error_reported:
                        await self.report_error(
                            "Bot returned no text in response",
                            {"message_id": message_id},
                        )
                    return
                elif event.event == "text":
                    text = await self._get_single_json_field(
                        event.data, "text", message_id
                    )
                elif event.event == "replace_response":
                    text = await self._get_single_json_field(
                        event.data, "replace_response", message_id
                    )
                    chunks.clear()
                elif event.event == "suggested_reply":
                    text = await self._get_single_json_field(
                        event.data, "suggested_reply", message_id
                    )
                    yield BotMessage(
                        text=text,
                        raw_response={"type": event.event, "text": event.data},
                        full_prompt=repr(request),
                        is_suggested_reply=True,
                    )
                    continue
                elif event.event == "meta":
                    if event_count != 1:
                        # spec says a meta event that is not the first event is ignored
                        continue
                    data = await self._load_json_dict(event.data, "meta", message_id)
                    linkify = data.get("linkify", False)
                    if not isinstance(linkify, bool):
                        await self.report_error(
                            "Invalid linkify value in 'meta' event",
                            {"message_id": message_id, "linkify": linkify},
                        )
                        error_reported = True
                        continue
                    send_suggested_replies = data.get("suggested_replies", False)
                    if not isinstance(send_suggested_replies, bool):
                        await self.report_error(
                            "Invalid suggested_replies value in 'meta' event",
                            {
                                "message_id": message_id,
                                "suggested_replies": send_suggested_replies,
                            },
                        )
                        error_reported = True
                        continue
                    content_type = data.get("content_type", "text/markdown")
                    if not isinstance(content_type, str):
                        await self.report_error(
                            "Invalid content_type value in 'meta' event",
                            {"message_id": message_id, "content_type": content_type},
                        )
                        error_reported = True
                        continue
                    yield MetaMessage(
                        text="",
                        raw_response=data,
                        full_prompt=repr(request),
                        linkify=linkify,
                        suggested_replies=send_suggested_replies,
                        content_type=cast(ContentType, content_type),
                    )
                    continue
                elif event.event == "error":
                    data = await self._load_json_dict(event.data, "error", message_id)
                    if data.get("allow_retry", True):
                        raise BotError(event.data)
                    else:
                        raise BotErrorNoRetry(event.data)
                elif event.event == "ping":
                    # Not formally part of the spec, but FastAPI sends this; let's ignore it
                    # instead of sending error reports.
                    continue
                else:
                    # Truncate the type and message in case it's huge.
                    await self.report_error(
                        f"Unknown event type: {_safe_ellipsis(event.event, 100)}",
                        {
                            "event_data": _safe_ellipsis(event.data, 500),
                            "message_id": message_id,
                        },
                    )
                    error_reported = True
                    continue
                chunks.append(text)
                yield BotMessage(
                    text=text,
                    raw_response={"type": event.event, "text": event.data},
                    full_prompt=repr(request),
                    is_replace_response=(event.event == "replace_response"),
                )
        await self.report_error(
            "Bot exited without sending 'done' event", {"message_id": message_id}
        )

    async def _get_single_json_field(
        self, data: str, context: str, message_id: Identifier, field: str = "text"
    ) -> str:
        data_dict = await self._load_json_dict(data, context, message_id)
        text = data_dict[field]
        if not isinstance(text, str):
            await self.report_error(
                f"Expected string in '{field}' field for '{context}' event",
                {"data": data_dict, "message_id": message_id},
            )
            raise BotErrorNoRetry(f"Expected string in '{context}' event")
        return text

    async def _load_json_dict(
        self, data: str, context: str, message_id: Identifier
    ) -> Dict[str, object]:
        try:
            parsed = json.loads(data)
        except json.JSONDecodeError:
            await self.report_error(
                f"Invalid JSON in {context!r} event",
                {"data": data, "message_id": message_id},
            )
            # If they are returning invalid JSON, retrying immediately probably won't help
            raise BotErrorNoRetry(f"Invalid JSON in {context!r} event")
        if not isinstance(parsed, dict):
            await self.report_error(
                f"Expected JSON dict in {context!r} event",
                {"data": data, "message_id": message_id},
            )
            raise BotError(f"Expected JSON dict in {context!r} event")
        return cast(Dict[str, object], parsed)


def _default_error_handler(e: Exception, msg: str) -> None:
    print("Error in Poe bot:", msg, e)


async def stream_request(
    request: QueryRequest,
    bot_name: str,
    api_key: str = "",
    *,
    access_key: str = "",
    access_key_deprecation_warning_stacklevel: int = 2,
    session: Optional[httpx.AsyncClient] = None,
    on_error: ErrorHandler = _default_error_handler,
    num_tries: int = 2,
    retry_sleep_time: float = 0.5,
    base_url: str = "https://api.poe.com/bot/",
) -> AsyncGenerator[PartialResponse, None]:
    """Streams BotMessages from a Poe bot."""
    if access_key != "":
        warnings.warn(
            "the access_key param is no longer necessary when using this function.",
            DeprecationWarning,
            stacklevel=access_key_deprecation_warning_stacklevel,
        )

    async with contextlib.AsyncExitStack() as stack:
        if session is None:
            session = await stack.enter_async_context(httpx.AsyncClient())
        url = f"{base_url}{bot_name}"
        ctx = _BotContext(
            endpoint=url, api_key=api_key, session=session, on_error=on_error
        )
        got_response = False
        for i in range(num_tries):
            try:
                async for message in ctx.perform_query_request(request):
                    got_response = True
                    yield message
                break
            except BotErrorNoRetry:
                raise
            except Exception as e:
                on_error(e, f"Bot request to {bot_name} failed on try {i}")
                if got_response or i == num_tries - 1:
                    # If it's a BotError, it probably has a good error message
                    # that we want to show directly.
                    if isinstance(e, BotError):
                        raise
                    # But if it's something else (maybe an HTTP error or something),
                    # wrap it in a BotError that makes it clear which bot is broken.
                    raise BotError(f"Error communicating with bot {bot_name}") from e
                await asyncio.sleep(retry_sleep_time)


def get_bot_response(
    messages: List[ProtocolMessage],
    bot_name: str,
    api_key: str,
    *,
    temperature: Optional[float] = None,
    skip_system_prompt: Optional[bool] = None,
    logit_bias: Optional[Dict[str, float]] = None,
    stop_sequences: Optional[List[str]] = None,
    base_url: str = "https://api.poe.com/bot/",
) -> AsyncGenerator[BotMessage, None]:
    additional_params = {}
    # This is so that we don't have to redefine the default values for these params.
    if temperature is not None:
        additional_params["temperature"] = temperature
    if skip_system_prompt is not None:
        additional_params["skip_system_prompt"] = skip_system_prompt
    if logit_bias is not None:
        additional_params["logit_bias"] = logit_bias
    if stop_sequences is not None:
        additional_params["stop_sequences"] = stop_sequences

    query = QueryRequest(
        query=messages,
        user_id="",
        conversation_id="",
        message_id="",
        version=PROTOCOL_VERSION,
        type="query",
        **additional_params,
    )
    return stream_request(
        request=query, bot_name=bot_name, api_key=api_key, base_url=base_url
    )


async def get_final_response(
    request: QueryRequest,
    bot_name: str,
    api_key: str = "",
    *,
    access_key: str = "",
    session: Optional[httpx.AsyncClient] = None,
    on_error: ErrorHandler = _default_error_handler,
    num_tries: int = 2,
    retry_sleep_time: float = 0.5,
    base_url: str = "https://api.poe.com/bot/",
) -> str:
    """Gets the final response from a Poe bot."""
    chunks: List[str] = []
    async for message in stream_request(
        request,
        bot_name,
        api_key,
        access_key=access_key,
        access_key_deprecation_warning_stacklevel=3,
        session=session,
        on_error=on_error,
        num_tries=num_tries,
        retry_sleep_time=retry_sleep_time,
        base_url=base_url,
    ):
        if isinstance(message, MetaMessage):
            continue
        if message.is_suggested_reply:
            continue
        if message.is_replace_response:
            chunks.clear()
        chunks.append(message.text)
    if not chunks:
        raise BotError(f"Bot {bot_name} sent no response")
    return "".join(chunks)


async def ask_poe_explain(text):
    total = ""
    message = ProtocolMessage(role="user", content="Split this text into sentences and explain the meaning, grammar pattern used and difficult words of each sentence:" + text )
    async for partial in get_bot_response(messages=[message], bot_name="Assistant", api_key="BWWP0zUenxCRm_SAY_LgQKfuJmR2gyMI4lIzm91suNk"): 
        print( partial.text, sep="")
        total += partial.text    
    return total


async def ask_poe_test_vocabulary(text):
    total = ""
    message = ProtocolMessage(role="user", content="Create a test to check if I know the vocabulary of this text:" + text )
    async for partial in get_bot_response(messages=[message], bot_name="Assistant", api_key="BWWP0zUenxCRm_SAY_LgQKfuJmR2gyMI4lIzm91suNk"): 
        print( partial.text, sep="")
        total += partial.text    
    return total


async def ask_poe_test_understanding(text):
    total = ""
    message = ProtocolMessage(role="user", content="Create a test with 10 questions to check my understanding of this text" + text )
    async for partial in get_bot_response(messages=[message], bot_name="Assistant", api_key="BWWP0zUenxCRm_SAY_LgQKfuJmR2gyMI4lIzm91suNk"): 
        print( partial.text, sep="")
        total += partial.text
    message = ProtocolMessage(role="user", content="Create a test with statements that are true or false based upon the text" + text )
    async for partial in get_bot_response(messages=[message], bot_name="Assistant", api_key="BWWP0zUenxCRm_SAY_LgQKfuJmR2gyMI4lIzm91suNk"): 
        print( partial.text, sep="")
        total += partial.text    
    message = ProtocolMessage(role="user", content="What are the main ideas in the text provided. Reply in traditional Chinese. Text:" + text )
    async for partial in get_bot_response(messages=[message], bot_name="Assistant", api_key="BWWP0zUenxCRm_SAY_LgQKfuJmR2gyMI4lIzm91suNk"): 
        print( partial.text, sep="")
        total += partial.text    

    return total



async def ask_poe_grammar_test(text):
    total = ""
    message = ProtocolMessage(role="user", content=" Give me a list of grammar patterns in this text. Split the name of the pattern and the example with '|':" + text )
    async for partial in get_bot_response(messages=[message], bot_name="GPT-4", api_key="BWWP0zUenxCRm_SAY_LgQKfuJmR2gyMI4lIzm91suNk"): 
        print( partial.text, sep="")
        total += partial.text
    rules = total.split("\n")
    output = text + "\n"
    for i in rules:
        if len(i.split('|')) == 2:
            output += i.split('|')[0] + "\n"
    output += "\n\n\n"
    for i in rules:
        if len(i.split('|')) == 2:
            output += i + "\n"
    return output




async def ask_poe_free(question,bot_name):
    total = ""
    message = ProtocolMessage(role="user", content= question )
    async for partial in get_bot_response(messages=[message], bot_name=bot_name, api_key="BWWP0zUenxCRm_SAY_LgQKfuJmR2gyMI4lIzm91suNk"): 
        print( partial.text, sep="")
        total += partial.text
    rules = total.split("\n")
    output = text + "\n"
    for i in rules:
        if len(i.split('|')) == 2:
            output += i.split('|')[0] + "\n"
    output += "\n\n\n"
    for i in rules:
        if len(i.split('|')) == 2:
            output += i + "\n"
    return output


async def testit():
    await test() 


async def test():
    message = ProtocolMessage(role="user", content=""" Give me a list of grammar patterns in this text. Split the name of the pattern and the example with '|':
廉政公署為一帶一路沿線國家舉辦為期7日的「大型基建反腐治理專業課程」，提供實地考察行程，並分享案例及防貪知識。

廉署表示，有21名來自13個非洲及亞洲國家的中高層反貪機構管理人員參與，香港及澳門亦分別有4名及2名代表參與。課程今日是最後一日，期間安排學員到訪本港機場，並到訪在明年啟用的深中通道及港珠澳大橋等項目，他們亦有與國家反貪機構交流，而廉署有分享案例及防貪知識，發展局亦有派員講述本港在發展項目的防貪措施。

有參與的非洲國家馬里代表說，當地的送禮文化普遍，當地人不會視貪污為大問題，形容觀察到內地在打擊貪污的法律框架水平高。至於南非代表就認為課程內容實用，超出預期。

廉署執行處首席調查主任柳智浩表示，一帶一路倡議中不少涉及大型基建項目，會涉及大量資金，因此希望透過今次課程提升沿線國家或地區反貪能力。他形容今次課程反應熱烈及成功，未來將繼續舉辦，預計會聚焦在財務調查及如何利用科技打擊貪污。

律政司司長林定國在結業儀式上表示，基建項目涉及大額款項，如涉及貪污會影響政府誠信及法治等，因此在重大基建項目加強反貪能力是有需要。他又引述國務院有關一帶一路白皮書，指出對貪污行為零容忍。

廉政專員胡英明表示，不同國家在應對貪污問題情況都不一樣，希望可透過課程加強各地機構間的合作，形容今次課程反映出廉署對國際反貪工作的承諾。
""")
    async for partial in get_bot_response(messages=[message], bot_name="GPT-4", api_key="BWWP0zUenxCRm_SAY_LgQKfuJmR2gyMI4lIzm91suNk"): 
        print(partial.text, end ="")
    
async def testit():
    await test() 


filename = sys.argv[2]
f = open(filename,"r")
text = f.read()
f.close()

filename = sys.argv[2]
f = open(filename+".debug","w")
f.write(str(sys.argv))
f.close()

guest = ''

if sys.argv[1] == "free":
    guest = asyncio.run(ask_poe_free(text,sys.argv[3]))
    print(guest)

if sys.argv[1] == "grammar":
    guest = asyncio.run(ask_poe_explain(text))
    print(guest)
if sys.argv[1] == "testvocabulary":
    guest = asyncio.run(ask_poe_test_vocabulary(text))
    print(guest)
if sys.argv[1] == "testunderstanding":
    guest = asyncio.run(ask_poe_test_understanding(text))
    print(guest)

f = open(filename+".res","w")
f.write(guest)
f.close()