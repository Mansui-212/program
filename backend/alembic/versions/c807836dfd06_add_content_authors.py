"""add content authors

Revision ID: c807836dfd06
Revises: 9fd467a31e83
Create Date: 2026-08-20 15:21:40.175364

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c807836dfd06'
down_revision: Union[str, Sequence[str], None] = '9fd467a31e83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('memes', sa.Column('author_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_memes_author_id'), 'memes', ['author_id'], unique=False)
    op.create_foreign_key(
        'fk_memes_author_id_users',
        'memes',
        'users',
        ['author_id'],
        ['id'],
    )
    op.add_column('music_tracks', sa.Column('author_id', sa.Integer(), nullable=True))
    op.create_index(op.f('ix_music_tracks_author_id'), 'music_tracks', ['author_id'], unique=False)
    op.create_foreign_key(
        'fk_music_tracks_author_id_users',
        'music_tracks',
        'users',
        ['author_id'],
        ['id'],
    )

    op.execute(
        """
        UPDATE memes AS meme
        INNER JOIN submissions AS submission
            ON submission.submission_type = 'meme'
            AND submission.content_id = meme.id
        SET meme.author_id = submission.user_id
        WHERE meme.author_id IS NULL
        """
    )
    op.execute(
        """
        UPDATE music_tracks AS track
        INNER JOIN submissions AS submission
            ON submission.submission_type = 'music'
            AND submission.content_id = track.id
        SET track.author_id = submission.user_id
        WHERE track.author_id IS NULL
        """
    )


def downgrade() -> None:
    op.drop_constraint('fk_music_tracks_author_id_users', 'music_tracks', type_='foreignkey')
    op.drop_index(op.f('ix_music_tracks_author_id'), table_name='music_tracks')
    op.drop_column('music_tracks', 'author_id')
    op.drop_constraint('fk_memes_author_id_users', 'memes', type_='foreignkey')
    op.drop_index(op.f('ix_memes_author_id'), table_name='memes')
    op.drop_column('memes', 'author_id')
