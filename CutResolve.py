import os
from tkinter import Tk, filedialog, Button, Label, Frame
from scenedetect import VideoManager, SceneManager
from scenedetect.detectors import ContentDetector
from datetime import timedelta

# Sensitivity for scene detection
THRESHOLD = 30.0

def seconds_to_timecode(seconds, fps=24):
    td = timedelta(seconds=seconds)
    total_frames = int(seconds * fps)
    hh, remainder = divmod(td.seconds, 3600)
    mm, ss = divmod(remainder, 60)
    ff = total_frames % fps
    return f"{hh:02d}:{mm:02d}:{ss:02d}:{ff:02d}"

def process_video():
    video_file = filedialog.askopenfilename(
        title="Select your video",
        filetypes=[("MP4 files", "*.mp4")]
    )
    if not video_file:
        return

    status_label.config(text="⏳ Processing... Please wait.")
    root.update_idletasks()

    folder = os.path.dirname(video_file)
    base_name = os.path.splitext(os.path.basename(video_file))[0]
    edl_file = os.path.join(folder, base_name + ".edl")  # Save in same folder

    # Scene detection
    video_manager = VideoManager([video_file])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=THRESHOLD))
    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager)
    scenes = scene_manager.get_scene_list()
    video_manager.release()

    print(f"Detected {len(scenes)} cuts in {video_file}")

    # --- EDL FILE HEADER ---
    edl_content = f"TITLE: {base_name}\nFCM: NON-DROP FRAME\n\n"

    # Build EDL events
    for i, scene in enumerate(scenes):
        start = scene[0].get_seconds()
        end = scene[1].get_seconds()

        start_tc = seconds_to_timecode(start)
        end_tc = seconds_to_timecode(end)

        edl_content += (
            f"{i+1:03d}  AX       V     C        {start_tc} {end_tc} {start_tc} {end_tc}\n"
            f"* FROM CLIP NAME: {base_name}\n"
        )

    # Save EDL
    with open(edl_file, "w", encoding="utf-8") as f:
        f.write(edl_content)

    print(f"✅ EDL script created: {edl_file}")
    status_label.config(text=f"✅ Done! EDL created: {edl_file}")

# --- GUI ---
root = Tk()
root.title("CutResolve - Auto Scene Cut Generator")
root.geometry("500x250")
root.resizable(False, False)
root.configure(bg="black")

frame = Frame(root, bg="black", padx=20, pady=20)
frame.pack(expand=True, fill="both")

resolve_gold = "#F7C600"
status_green = "#00FF7F"
footer_gray = "#AAAAAA"

header_label = Label(
    frame, text="CutResolve - Auto Scene Cut Generator",
    font=("Helvetica", 18, "bold"), fg=resolve_gold, bg="black"
)
header_label.pack(pady=(0, 20))

upload_button = Button(
    frame, text="Upload Your Video", command=process_video,
    width=30, height=2, bg=resolve_gold, fg="black", activebackground="black", activeforeground="white"
)
upload_button.pack(pady=10)

status_label = Label(frame, text="", font=("Helvetica", 10), fg=status_green, bg="black")
status_label.pack(pady=10)

footer_label = Label(frame, text="Created by Vincent Ilagan (CutResolve Edition)", font=("Helvetica", 10, "italic"), fg=footer_gray, bg="black")
footer_label.pack(side="bottom", pady=(15,0))

root.mainloop()
