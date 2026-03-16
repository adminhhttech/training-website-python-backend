from moviepy import ImageClip, AudioFileClip, concatenate_videoclips


def build_video(slides, audios, output, fps):
    clips = []
    
    for slide, audio in zip(slides, audios):
        audio_clip = AudioFileClip(audio)
        clip = (
            ImageClip(slide)
            .with_duration(audio_clip.duration)
            .with_audio(audio_clip)
        )
        clips.append(clip)
    
    # Concatenate all clips
    final_video = concatenate_videoclips(clips)
    
    # Ensure video is maximum 60 seconds
    if final_video.duration > 60.0:
        final_video = final_video.subclipped(0, 60.0)
    
    final_video.write_videofile(output, fps=fps)
