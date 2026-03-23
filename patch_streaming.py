with open('streaming_service/streaming/views.py', 'r') as f:
    content = f.read()

import_statement = "from shared.events import event_bus\n"
if "from shared.events import event_bus" not in content:
    content = content.replace("from shared.jwt_utils import decode_token, generate_signed_url", 
                              "from shared.jwt_utils import decode_token, generate_signed_url\n" + import_statement)

start_stream_patch = """
    # Generate signed URL for the master playlist
    playlist_path = f"/api/streaming/hls/{movie_id}/master.m3u8"
    signed_url = generate_signed_url(playlist_path)

    # Publish video_played event
    try:
        event_bus.publish('video_events', 'video_started', {
            'user_id': payload['user_id'],
            'movie_id': movie_id,
            'session_token': session_token
        })
    except Exception:
        pass
"""

if "event_bus.publish('video_events', 'video_started'" not in content:
    content = content.replace("""    # Generate signed URL for the master playlist
    playlist_path = f"/api/streaming/hls/{movie_id}/master.m3u8"
    signed_url = generate_signed_url(playlist_path)""", start_stream_patch)


end_stream_patch = """
    try:
        session = StreamSession.objects.get(session_token=session_token)
        session.is_active = False
        session.save()
        
        # Publish video_ended event
        try:
            event_bus.publish('video_events', 'video_ended', {
                'user_id': session.user_id,
                'movie_id': session.movie_id,
                'session_token': session_token
            })
        except Exception:
            pass

        return Response({'status': 'ended'})
"""

if "event_bus.publish('video_events', 'video_ended'" not in content:
    content = content.replace("""    try:
        session = StreamSession.objects.get(session_token=session_token)
        session.is_active = False
        session.save()
        return Response({'status': 'ended'})""", end_stream_patch)

with open('streaming_service/streaming/views.py', 'w') as f:
    f.write(content)
