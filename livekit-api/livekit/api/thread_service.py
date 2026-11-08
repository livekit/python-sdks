from __future__ import annotations

from livekit.protocol.agent_pb.agent_thread import AgentTask, AgentThread

from ._generated.public_api.models import (
    LivekitAgentAgentTaskStatus,
    LivekitPublicapiCommonV1SortOrder,
    ThreadServiceCreateThreadBody,
    ThreadServiceUpdateThreadBody,
)
from ._service import PublicApiService
from .public_api_client import from_json, next_cursor, opt, page_size, to_json

_SORT_ORDERS = {
    AgentThread.SORT_ORDER_ASC: LivekitPublicapiCommonV1SortOrder.SORT_ORDER_ASC,
    AgentThread.SORT_ORDER_DESC: LivekitPublicapiCommonV1SortOrder.SORT_ORDER_DESC,
}


class ThreadService(PublicApiService):
    """Agent threads: conversations whose chat items, tasks and database outlive any one session.

    Recommended way to use this service is via `livekit.api.LiveKitAPI`:

    ```python
    from livekit import api
    lkapi = api.LiveKitAPI()
    thread = await lkapi.threads.create_thread(api.AgentThread.CreateRequest(scope="user_42"))
    ```
    """

    async def create_thread(self, req: AgentThread.CreateRequest) -> AgentThread.Thread:
        """Creates a thread and its database."""
        res = await self._request(
            self._client.threads.thread_service_create_thread_without_preload_content,
            thread_service_create_thread_body=ThreadServiceCreateThreadBody.from_dict(to_json(req)),
        )
        return from_json(res.get("thread"), AgentThread.Thread())

    async def get_thread(self, thread_id: str) -> AgentThread.Thread:
        res = await self._request(
            self._client.threads.thread_service_get_thread_without_preload_content,
            thread_id=thread_id,
        )
        return from_json(res.get("thread"), AgentThread.Thread())

    async def list_threads(self, req: AgentThread.ListRequest) -> AgentThread.ListResponse:
        """The threads of one scope (every scope when empty), newest first."""
        res = await self._request(
            self._client.threads.thread_service_list_threads_without_preload_content,
            scope=opt(req.scope),
            page_cursor=opt(req.page_token),
            page_page_size=page_size(req.limit),
        )
        return from_json(
            {"threads": res.get("items"), "nextPageToken": next_cursor(res)},
            AgentThread.ListResponse(),
        )

    async def update_thread(self, req: AgentThread.UpdateRequest) -> AgentThread.Thread:
        """Merges the thread's attributes (an empty value deletes the entry) and sets its idle
        TTL. An update counts as activity."""
        body = to_json(req)
        body.pop("threadId", None)
        res = await self._request(
            self._client.threads.thread_service_update_thread_without_preload_content,
            thread_id=req.thread_id,
            thread_service_update_thread_body=ThreadServiceUpdateThreadBody.from_dict(body),
        )
        return from_json(res.get("thread"), AgentThread.Thread())

    async def delete_thread(self, thread_id: str) -> None:
        """Deletes the thread and its database."""
        await self._request(
            self._client.threads.thread_service_delete_thread_without_preload_content,
            thread_id=thread_id,
        )

    async def get_thread_items(
        self, req: AgentThread.GetItemsRequest
    ) -> AgentThread.GetItemsResponse:
        """The thread's chat items, oldest first unless `sort_order` says otherwise."""
        res = await self._request(
            self._client.threads.thread_service_get_thread_items_without_preload_content,
            thread_id=req.thread_id,
            agent=opt(req.agent),
            page_cursor=opt(req.page_token),
            page_page_size=page_size(req.limit),
            sort_order=_SORT_ORDERS.get(req.sort_order),
        )
        return from_json(
            {"items": res.get("items"), "nextPageToken": next_cursor(res)},
            AgentThread.GetItemsResponse(),
        )

    async def get_thread_tasks(self, req: AgentTask.GetTasksRequest) -> AgentTask.GetTasksResponse:
        """The thread's tasks, oldest first."""
        status = (
            LivekitAgentAgentTaskStatus(AgentTask.Status.Name(req.status))
            if req.HasField("status")
            else None
        )
        res = await self._request(
            self._client.threads.thread_service_get_thread_tasks_without_preload_content,
            thread_id=req.thread_id,
            status=status,
            page_cursor=opt(req.page_token),
            page_page_size=page_size(req.limit),
        )
        return from_json(
            {"tasks": res.get("items"), "nextPageToken": next_cursor(res)},
            AgentTask.GetTasksResponse(),
        )
