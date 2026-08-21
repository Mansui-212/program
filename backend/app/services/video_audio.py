import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4


PROJECT_ROOT = Path(__file__).resolve().parents[3]
STORAGE_DIR = PROJECT_ROOT / "storage"
TRACK_DIR = STORAGE_DIR / "audio" / "tracks"
COVER_DIR = STORAGE_DIR / "images" / "music-covers"
TEMP_IMPORT_DIR = STORAGE_DIR / "temp" / "video-imports"


class VideoAudioError(ValueError):
    """A user-facing error raised when a video cannot become a music track."""


@dataclass(frozen=True)
class VideoMusicAssets:
    audio_url: str
    cover_url: str
    duration_seconds: int | None


def require_media_binaries() -> tuple[str, str]:
    ffmpeg = shutil.which("ffmpeg")
    ffprobe = shutil.which("ffprobe")

    if ffmpeg is None or ffprobe is None:
        raise VideoAudioError("音视频处理服务暂不可用，请稍后重试")

    return ffmpeg, ffprobe


def extract_music_from_video(video_path: Path) -> VideoMusicAssets:
    """Extract a complete audio track and a cover frame, then remove the source video."""
    ffmpeg, ffprobe = require_media_binaries()
    job_dir = TEMP_IMPORT_DIR / uuid4().hex
    job_dir.mkdir(parents=True, exist_ok=False)
    extracted_audio = job_dir / "track.mp3"
    extracted_cover = job_dir / "cover.jpg"

    try:
        probe = subprocess.run(
            [
                ffprobe,
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-show_streams",
                "-of",
                "json",
                str(video_path),
            ],
            capture_output=True,
            text=True,
            timeout=45,
            check=False,
        )
        if probe.returncode != 0:
            raise VideoAudioError("无法读取视频文件，请确认文件未损坏")

        try:
            media_info = json.loads(probe.stdout)
        except json.JSONDecodeError as error:
            raise VideoAudioError("无法读取视频文件，请确认文件未损坏") from error

        streams = media_info.get("streams", [])
        has_video = any(stream.get("codec_type") == "video" for stream in streams)
        has_audio = any(stream.get("codec_type") == "audio" for stream in streams)
        if not has_video:
            raise VideoAudioError("上传文件不是可用的视频")
        if not has_audio:
            raise VideoAudioError("该视频没有可提取的音轨")

        duration_value = media_info.get("format", {}).get("duration")
        try:
            duration_seconds = max(0, round(float(duration_value)))
        except (TypeError, ValueError):
            duration_seconds = None
        cover_offset = min(1, (duration_seconds or 0) / 2)

        audio_result = subprocess.run(
            [
                ffmpeg,
                "-y",
                "-i",
                str(video_path),
                "-vn",
                "-c:a",
                "libmp3lame",
                "-b:a",
                "192k",
                str(extracted_audio),
            ],
            capture_output=True,
            text=True,
            timeout=300,
            check=False,
        )
        if audio_result.returncode != 0 or not extracted_audio.is_file():
            raise VideoAudioError("音频提取失败，请换一个视频文件后重试")

        cover_result = subprocess.run(
            [
                ffmpeg,
                "-y",
                "-ss",
                str(cover_offset),
                "-i",
                str(video_path),
                "-frames:v",
                "1",
                "-q:v",
                "2",
                str(extracted_cover),
            ],
            capture_output=True,
            text=True,
            timeout=90,
            check=False,
        )
        if cover_result.returncode != 0 or not extracted_cover.is_file():
            raise VideoAudioError("封面生成失败，请换一个视频文件后重试")

        TRACK_DIR.mkdir(parents=True, exist_ok=True)
        COVER_DIR.mkdir(parents=True, exist_ok=True)
        audio_name = f"video_{uuid4().hex}.mp3"
        cover_name = f"video_{uuid4().hex}.jpg"
        target_audio = TRACK_DIR / audio_name
        target_cover = COVER_DIR / cover_name
        shutil.move(str(extracted_audio), target_audio)
        shutil.move(str(extracted_cover), target_cover)

        return VideoMusicAssets(
            audio_url=f"/static/audio/tracks/{audio_name}",
            cover_url=f"/static/images/music-covers/{cover_name}",
            duration_seconds=duration_seconds,
        )
    except subprocess.TimeoutExpired as error:
        raise VideoAudioError("视频处理超时，请换较短的视频后重试") from error
    except OSError as error:
        raise VideoAudioError("音视频处理服务暂不可用，请稍后重试") from error
    finally:
        video_path.unlink(missing_ok=True)
        shutil.rmtree(job_dir, ignore_errors=True)


def remove_generated_music_assets(audio_url: str, cover_url: str | None) -> None:
    paths = (
        (audio_url, "/static/audio/tracks/", TRACK_DIR),
        (cover_url, "/static/images/music-covers/", COVER_DIR),
    )

    for static_url, prefix, directory in paths:
        if not static_url or not static_url.startswith(prefix):
            continue

        candidate = (directory / static_url.removeprefix(prefix)).resolve()
        try:
            candidate.relative_to(directory.resolve())
        except ValueError:
            continue

        if candidate.is_file():
            candidate.unlink()
