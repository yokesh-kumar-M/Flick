from celery import shared_task
import subprocess
import os
import logging
from django.utils import timezone

logger = logging.getLogger(__name__)

@shared_task(bind=True)
def transcode_video(self, job_id):
    """Enterprise-grade single-pass ABR Transcode using FFmpeg."""
    from .models import TranscodeJob

    try:
        job = TranscodeJob.objects.get(pk=job_id)
        job.status = 'processing'
        job.save()

        source = job.source_file
        output_dir = job.output_dir or f"media/hls/{job.movie_id}"
        os.makedirs(output_dir, exist_ok=True)

        # Create stream subdirectories for FFmpeg to write into
        for stream_name in ['1080p', '720p', '480p', '360p']:
            os.makedirs(os.path.join(output_dir, stream_name), exist_ok=True)

        # Advanced FFmpeg ABR filtergraph
        cmd = [
            'ffmpeg', '-hide_banner', '-y', '-i', source,
            '-filter_complex', 
            '[0:v]split=4[v1][v2][v3][v4]; '
            '[v1]scale=w=-2:h=1080[v1out]; '
            '[v2]scale=w=-2:h=720[v2out]; '
            '[v3]scale=w=-2:h=480[v3out]; '
            '[v4]scale=w=-2:h=360[v4out]',
            
            # Video encodings
            '-map', '[v1out]', '-c:v:0', 'libx264', '-preset', 'veryfast', '-b:v:0', '5000k', '-maxrate:v:0', '5350k', '-bufsize:v:0', '7500k', '-g', '48', '-keyint_min', '48', '-sc_threshold', '0',
            '-map', '[v2out]', '-c:v:1', 'libx264', '-preset', 'veryfast', '-b:v:1', '2800k', '-maxrate:v:1', '2996k', '-bufsize:v:1', '4200k', '-g', '48', '-keyint_min', '48', '-sc_threshold', '0',
            '-map', '[v3out]', '-c:v:2', 'libx264', '-preset', 'veryfast', '-b:v:2', '1400k', '-maxrate:v:2', '1498k', '-bufsize:v:2', '2100k', '-g', '48', '-keyint_min', '48', '-sc_threshold', '0',
            '-map', '[v4out]', '-c:v:3', 'libx264', '-preset', 'veryfast', '-b:v:3', '800k', '-maxrate:v:3', '856k', '-bufsize:v:3', '1200k', '-g', '48', '-keyint_min', '48', '-sc_threshold', '0',
            
            # Audio encodings
            '-map', 'a:0', '-c:a:0', 'aac', '-b:a:0', '192k', '-ac', '2',
            '-map', 'a:0', '-c:a:1', 'aac', '-b:a:1', '128k', '-ac', '2',
            '-map', 'a:0', '-c:a:2', 'aac', '-b:a:2', '128k', '-ac', '2',
            '-map', 'a:0', '-c:a:3', 'aac', '-b:a:3', '96k', '-ac', '2',
            
            # HLS settings
            '-f', 'hls',
            '-hls_time', '6',
            '-hls_playlist_type', 'vod',
            '-hls_flags', 'independent_segments',
            '-hls_segment_type', 'mpegts',
            '-hls_segment_filename', os.path.join(output_dir, '%v', 'segment_%03d.ts'),
            '-master_pl_name', 'master.m3u8',
            '-var_stream_map', 'v:0,a:0,name:1080p v:1,a:1,name:720p v:2,a:2,name:480p v:3,a:3,name:360p',
            os.path.join(output_dir, '%v', 'index.m3u8')
        ]

        logger.info(f"Starting ABR transcode for job {job_id}")
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg transcode failed: {result.stderr[-1000:]}")

        job.status = 'completed'
        job.progress = 100
        job.output_dir = output_dir
        job.completed_at = timezone.now()
        job.save()

        logger.info(f"Transcode completed successfully for movie {job.movie_id}")

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
