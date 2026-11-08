from __future__ import annotations

from google.protobuf.empty_pb2 import Empty
from livekit.protocol.agent_pb.agent_thread import AgentTask, AgentThread

from ._generated.public_api.models import (
    LivekitAgentAgentTaskStatus,
    LivekitPublicapiCommonV1SortOrder,
    ThreadServiceCreateThreadBody,
    ThreadServiceUpdateThreadBody,
)
from ._service import PublicApiService
from .public_api_client import to_json

Thread = AgentThread.Thread
ThreadItem = AgentThread.Item
ThreadTask = AgentTask.Task
ThreadSortOrder = AgentThread.SortOrder
ThreadTaskStatus = AgentTask.Status
CreateThreadRequest = AgentThread.CreateRequest
ListThreadsRequest = AgentThread.ListRequest
ListThreadsResponse = AgentThread.ListResponse
UpdateThreadRequest = AgentThread.UpdateRequest
GetThreadItemsRequest = AgentThread.GetItemsRequest
GetThreadItemsResponse = AgentThread.GetItemsResponse
GetThreadTasksRequest = AgentTask.GetTasksRequest
GetThreadTasksResponse = AgentTask.GetTasksResponse

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
    thread = await lkapi.threads.create_thread(api.CreateThreadRequest(scope="user_42"))
    ```
    """

    async def create_thread(self, req: CreateThreadRequest) -> Thread:
        """Creates a thread and its database."""
        return await self._client.request(
            operation=self._client.threads.thread_service_create_thread_without_preload_content,
            headers=self._auth_header(),
            response_class=Thread,
            field="thread",
            thread_service_create_thread_body=ThreadServiceCreateThreadBody.from_dict(to_json(req)),
        )

    async def get_thread(self, *, thread_id: str) -> Thread:
        return await self._client.request(
            operation=self._client.threads.thread_service_get_thread_without_preload_content,
            headers=self._auth_header(),
            response_class=Thread,
            field="thread",
            thread_id=thread_id,
        )

    async def list_threads(self, req: ListThreadsRequest) -> ListThreadsResponse:
        """The threads of one scope (every scope when empty), newest first."""
        return await self._client.list(
            operation=self._client.threads.thread_service_list_threads_without_preload_content,
            headers=self._auth_header(),
            response_class=ListThreadsResponse,
            items="threads",
            page_token=req.page_token,
            limit=req.limit,
            scope=req.scope,
        )

    async def update_thread(self, req: UpdateThreadRequest) -> Thread:
        """Merges the thread's attributes (an empty value deletes the entry) and sets its idle
        TTL. An update counts as activity."""
        body = to_json(req)
        body.pop("threadId", None)
        return await self._client.request(
            operation=self._client.threads.thread_service_update_thread_without_preload_content,
            headers=self._auth_header(),
            response_class=Thread,
            field="thread",
            thread_id=req.thread_id,
            thread_service_update_thread_body=ThreadServiceUpdateThreadBody.from_dict(body),
        )

    async def delete_thread(self, *, thread_id: str) -> None:
        """Deletes the thread and its database."""
        await self._client.request(
            operation=self._client.threads.thread_service_delete_thread_without_preload_content,
            headers=self._auth_header(),
            response_class=Empty,
            thread_id=thread_id,
        )

    async def get_thread_items(self, req: GetThreadItemsRequest) -> GetThreadItemsResponse:
        """The thread's chat items, oldest first unless `sort_order` says otherwise."""
        return await self._client.list(
            operation=self._client.threads.thread_service_get_thread_items_without_preload_content,
            headers=self._auth_header(),
            response_class=GetThreadItemsResponse,
            items="items",
            page_token=req.page_token,
            limit=req.limit,
            thread_id=req.thread_id,
            agent=req.agent,
            sort_order=_SORT_ORDERS.get(req.sort_order),
        )

    async def get_thread_tasks(self, req: GetThreadTasksRequest) -> GetThreadTasksResponse:
        """The thread's tasks, oldest first."""
        status = (
            LivekitAgentAgentTaskStatus(ThreadTaskStatus.Name(req.status))
            if req.HasField("status")
            else None
        )
        return await self._client.list(
            operation=self._client.threads.thread_service_get_thread_tasks_without_preload_content,
            headers=self._auth_header(),
            response_class=GetThreadTasksResponse,
            items="tasks",
            page_token=req.page_token,
            limit=req.limit,
            thread_id=req.thread_id,
            status=status,
        )
