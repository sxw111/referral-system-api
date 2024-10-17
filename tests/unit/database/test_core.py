import pytest

from app.database import core


@pytest.mark.unit
class TestDatabase:
    """Class to verify the functionality of the database module."""

    @pytest.mark.asyncio
    async def test_get_database(self) -> None:
        """Ensure that an asynchronous database session is retrieved."""
        database = core.get_db()
        assert database is not None
        assert isinstance(database, core.AsyncGenerator)

        session = await database.__anext__()
        assert session is not None
        assert isinstance(session, core.AsyncSession)
