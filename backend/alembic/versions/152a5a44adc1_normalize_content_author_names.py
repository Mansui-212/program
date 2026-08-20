"""normalize content author names

Revision ID: 152a5a44adc1
Revises: c807836dfd06
Create Date: 2026-08-20 15:22:49.776179

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '152a5a44adc1'
down_revision: Union[str, Sequence[str], None] = 'c807836dfd06'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE memes AS meme
        INNER JOIN users AS user ON user.id = meme.author_id
        SET meme.author_name = user.username
        WHERE meme.author_id IS NOT NULL
        """
    )
    op.execute(
        """
        UPDATE music_tracks AS track
        INNER JOIN users AS user ON user.id = track.author_id
        SET track.author_name = user.username
        WHERE track.author_id IS NOT NULL
        """
    )


def downgrade() -> None:
    # Account names are presentation data for published content. Keep the
    # normalized values if this migration is rolled back.
    pass
