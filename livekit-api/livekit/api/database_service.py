from __future__ import annotations

from livekit.protocol.agentdb import AgentDB

from ._public_api.models import DatabaseServiceCreateDatabaseBody
from ._service import PublicApiService
from .public_api_client import from_json, next_cursor, opt, page_size, to_json


class DatabaseService(PublicApiService):
    """Agent databases of the project. Served by the LiveKit Cloud Public API.

    Recommended way to use this service is via `livekit.api.LiveKitAPI`:

    ```python
    from livekit import api
    lkapi = api.LiveKitAPI()
    databases = lkapi.databases
    ```
    """

    async def create(self, req: AgentDB.CreateRequest) -> AgentDB.CreateResponse:
        """Creates an empty database. Not idempotent: a retry creates a second one."""
        res = await self._client.request(
            self._client.databases.database_service_create_database_without_preload_content,
            database_service_create_database_body=DatabaseServiceCreateDatabaseBody.from_dict(
                to_json(req)
            ),
            headers=self._auth_header(),
        )
        return from_json(res, AgentDB.CreateResponse())

    async def get(self, database_id: str) -> AgentDB.AgentDatabase:
        res = await self._client.request(
            self._client.databases.database_service_get_database_without_preload_content,
            database_id=database_id,
            headers=self._auth_header(),
        )
        return from_json(res.get("database"), AgentDB.AgentDatabase())

    async def list(self, req: AgentDB.ListRequest) -> AgentDB.ListResponse:
        res = await self._client.request(
            self._client.databases.database_service_list_databases_without_preload_content,
            page_cursor=opt(req.page_token),
            page_page_size=page_size(req.page_size),
            headers=self._auth_header(),
        )
        return from_json(
            {"databases": res.get("items"), "nextPageToken": next_cursor(res)},
            AgentDB.ListResponse(),
        )

    async def delete(self, database_id: str) -> None:
        """Deletes the database, with its data and its metadata."""
        await self._client.request(
            self._client.databases.database_service_delete_database_without_preload_content,
            database_id=database_id,
            headers=self._auth_header(),
        )

    async def export(self, database_id: str) -> AgentDB.ExportResponse:
        """A pre-authenticated download URL of a consistent snapshot of the database."""
        res = await self._client.request(
            self._client.databases.database_service_export_database_without_preload_content,
            database_id=database_id,
            headers=self._auth_header(),
        )
        return from_json(res, AgentDB.ExportResponse())
