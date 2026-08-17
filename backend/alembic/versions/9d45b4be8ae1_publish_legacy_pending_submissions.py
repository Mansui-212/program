"""publish legacy pending submissions

Revision ID: 9d45b4be8ae1
Revises: d3bc49e1bacb
Create Date: 2026-08-17 14:02:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9d45b4be8ae1"
down_revision: Union[str, Sequence[str], None] = "d3bc49e1bacb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PUBLISH_HAKI_VALUE = 10


def upgrade() -> None:
    """Publish pre-stage-19 pending submissions through the new direct flow."""
    bind = op.get_bind()
    submissions = bind.execute(
        sa.text(
            """
            SELECT id, user_id, submission_type, title, description, file_url,
                   cover_url, character_id, source_name, source_url, author_name
            FROM submissions
            WHERE status = 'pending' AND content_id IS NULL AND content_deleted = 0
            ORDER BY id ASC
            """
        )
    ).mappings()

    for submission in submissions:
        if submission["submission_type"] == "meme":
            content_id = bind.execute(
                sa.text(
                    """
                    INSERT INTO memes (
                        slug, title, description, image_url, file_type, character_id,
                        source_name, source_url, author_name, view_count, download_count,
                        sort_order, is_featured
                    ) VALUES (
                        :slug, :title, :description, :file_url, :file_type, :character_id,
                        :source_name, :source_url, :author_name, 0, 0, 0, 0
                    )
                    """
                ),
                {
                    "slug": f"submission-meme-{submission['id']}",
                    "title": submission["title"][:120],
                    "description": submission["description"],
                    "file_url": submission["file_url"],
                    "file_type": "gif" if submission["file_url"].lower().endswith(".gif") else "image",
                    "character_id": submission["character_id"],
                    "source_name": submission["source_name"] or "用户投稿",
                    "source_url": submission["source_url"],
                    "author_name": submission["author_name"],
                },
            ).lastrowid
        elif submission["submission_type"] == "music":
            content_id = bind.execute(
                sa.text(
                    """
                    INSERT INTO music_tracks (
                        slug, title, description, audio_url, cover_url, duration_seconds,
                        character_id, original_title, source_name, source_url, author_name,
                        play_count, sort_order, is_featured
                    ) VALUES (
                        :slug, :title, :description, :file_url, :cover_url, NULL,
                        :character_id, NULL, :source_name, :source_url, :author_name,
                        0, 0, 0
                    )
                    """
                ),
                {
                    "slug": f"submission-music-{submission['id']}",
                    "title": submission["title"],
                    "description": submission["description"],
                    "file_url": submission["file_url"],
                    "cover_url": submission["cover_url"],
                    "character_id": submission["character_id"],
                    "source_name": submission["source_name"] or "用户投稿",
                    "source_url": submission["source_url"],
                    "author_name": submission["author_name"],
                },
            ).lastrowid
        else:
            continue

        bind.execute(
            sa.text(
                """
                UPDATE submissions
                SET status = 'approved', content_id = :content_id, content_deleted = 0
                WHERE id = :submission_id
                """
            ),
            {
                "content_id": content_id,
                "submission_id": submission["id"],
            },
        )
        bind.execute(
            sa.text("UPDATE users SET haki_value = haki_value + :value WHERE id = :user_id"),
            {
                "value": PUBLISH_HAKI_VALUE,
                "user_id": submission["user_id"],
            },
        )
        bind.execute(
            sa.text(
                """
                INSERT INTO haki_records (user_id, change_value, reason)
                VALUES (:user_id, :change_value, :reason)
                """
            ),
            {
                "user_id": submission["user_id"],
                "change_value": PUBLISH_HAKI_VALUE,
                "reason": f"历史作品发布：{submission['title']}"[:255],
            },
        )


def downgrade() -> None:
    """Keep already-published user content intact on downgrade."""
