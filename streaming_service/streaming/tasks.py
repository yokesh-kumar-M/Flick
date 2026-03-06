from celery import shared_task
import subprocess
import os
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True)
def transcode_video(self, job_id):
    """Transcode a video file to HLS format with multiple quality levels."""
    from .models import TranscodeJob
    from django.utils import timezone

    try:
        job = TranscodeJob.objects.get(pk=job_id)
        job.status = 'processing'
        job.save()

        source = job.source_file
        output_dir = job.output_dir or f"media/hls/{job.movie_id}"
        os.makedirs(output_dir, exist_ok=True)

        # Quality presets
        qualities = [
            {'name': '360p', 'height': 360, 'bitrate': '800k', 'audio': '96k'},
            {'name': '480p', 'height': 480, 'bitrate': '1400k', 'audio': '128k'},
            {'name': '720p', 'height': 720, 'bitrate': '2800k', 'audio': '128k'},
            {'name': '1080p', 'height': 1080, 'bitrate': '5000k', 'audio': '192k'},
        ]

        master_playlist = "#EXTM3U\n#EXT-X-VERSION:3\n"

        for q in qualities:
            q_dir = os.path.join(output_dir, q['name'])
            os.makedirs(q_dir, exist_ok=True)
            playlist_path = os.path.join(q_dir, 'index.m3u8')

            cmd = [
                'ffmpeg', '-i', source,
                '-vf', f"scale=-2:{q['height']}",
                '-c:v', 'libx264', '-preset', 'fast',
                '-b:v', q['bitrate'],
                '-c:a', 'aac', '-b:a', q['audio'],
                '-hls_time', '6',
                '-hls_list_size', '0',
                '-hls_segment_filename', os.path.join(q_dir, 'segment_%03d.ts'),
                '-f', 'hls',
                playlist_path,
                '-y'
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
            if result.returncode != 0:
                raise Exception(f"FFmpeg error for {q['name']}: {result.stderr[:500]}")

            bandwidth = int(q['bitrate'].replace('k', '')) * 1000
            master_playlist += f"#EXT-X-STREAM-INF:BANDWIDTH={bandwidth},RESOLUTION={q['height']}p\n"
            master_playlist += f"{q['name']}/index.m3u8\n"

        # Write master playlist
        with open(os.path.join(output_dir, 'master.m3u8'), 'w') as f:
            f.write(master_playlist)

        job.status = 'completed'
        job.progress = 100
        job.output_dir = output_dir
        job.completed_at = timezone.now()
        job.save()

        logger.info(f"Transcode completed for movie {job.movie_id}")

    except Exception as e:
        logger.error(f"Transcode failed for job {job_id}: {e}")
        try:
            job = TranscodeJob.objects.get(pk=job_id)
            job.status = 'failed'
            job.error_message = str(e)
            job.save()
        except Exception:
            pass
        raise
