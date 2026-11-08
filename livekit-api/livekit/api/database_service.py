from __future__ import annotations

from google.protobuf.empty_pb2 import Empty
from livekit.protocol.agentdb import AgentDB

from ._generated.public_api.models import DatabaseServiceCreateDatabaseBody
from ._service import PublicApiService
from .public_api_client import to_json


class DatabaseService(PublicApiService):
    """Agent databases.

    Recommended way to use this service is via `livekit.api.LiveKitAPI`:

    ```python
    from livekit import api
    lkapi = api.LiveKitAPI()
    database = await lkapi.databases.get_database("DB_...")
    ```
    """

    async def create_database(self, req: AgentDB.CreateRequest) -> AgentDB.CreateResponse:
        """Creates an empty database. Not idempotent: a retry creates a second one."""
        return await self._client.request(
            operation=self._client.databases.database_service_create_database_without_preload_content,
            headers=self._auth_header(),
            response_class=AgentDB.CreateResponse,
            database_service_create_database_body=DatabaseServiceCreateDatabaseBody.from_dict(
                to_json(req)
            ),
        )

    async def get_database(self, database_id: str) -> AgentDB.AgentDatabase:
        return await self._client.request(
            operation=self._client.databases.database_service_get_database_without_preload_content,
            headers=self._auth_header(),
            response_class=AgentDB.AgentDatabase,
            field="database",
            database_id=database_id,
        )

    async def list_databases(self, req: AgentDB.ListRequest) -> AgentDB.ListResponse:
        return await self._client.list(
            operation=self._client.databases.database_service_list_databases_without_preload_content,
            headers=self._auth_header(),
            response_class=AgentDB.ListResponse,
            items="databases",
            page_token=req.page_token,
            limit=req.page_size,
        )

    async def delete_database(self, database_id: str) -> None:
        """Deletes the database with its data."""
        await self._client.request(
            operation=self._client.databases.database_service_delete_database_without_preload_content,
            headers=self._auth_header(),
            response_class=Empty,
            database_id=database_id,
        )

    async def export_database(self, database_id: str) -> AgentDB.ExportResponse:
        """A pre-authenticated download URL of a consistent snapshot of the database."""
        return await self._client.request(
            operation=self._client.databases.database_service_export_database_without_preload_content,
            headers=self._auth_header(),
            response_class=AgentDB.ExportResponse,
            database_id=database_id,
        )
