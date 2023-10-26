import pytube, random, time, os, vlc, moviepy.editor, threading, urllib
from PIL import Image

import customtkinter as CTk

thread_avalibility = [True,True]
def changePlaylist():
    global p
    p = pytube.Playlist(play.get())
    play.set("")
    
def songLoop():
    global ready_for_song, prepare_next_song_thread_first, prepare_next_song_thread_second, thread_avalibility
    if(len(qued_songs) > 0):
        try:
            if thread_avalibility[0]:
                thread_avalibility[0] = False
                prepare_next_song_thread_first = threading.Thread(target=prepare_next_song, args=(1,))
                prepare_next_song_thread_first.start()
        except Exception as e:
            print(e)
            
    else:
        prepare_next_song(0)
    play_next_song()
    print("Odsd")
    ready_for_song = True
    if(len(qued_songs)  < 5):
        try:
            if thread_avalibility[1]:
                thread_avalibility[1] = False
                prepare_next_song_thread_second = threading.Thread(target=prepare_next_song, args=(2,))
                prepare_next_song_thread_second.start()
        except Exception as e:
            print(e)
        print("Double buffering")
    skipButton.configure(text_color="#0191DF")
    ready_for_song = True
        
def prepare_next_song(thread):   
    global qued_song_picture, thread_avalibility
    print(thread)
    for _ in range(5):
        try:
            url = random.choice(p)
            currentVideo = pytube.YouTube(url)
            picture_url = currentVideo.thumbnail_url
            audio_stream = currentVideo.streams.get_audio_only()
            print(audio_stream)
            print(picture_url)
            downloadFile = audio_stream.download(output_path=os.path.join(os.getcwd(), "music"))
            base, ext = os.path.splitext(downloadFile)
            base_name = os.path.basename(downloadFile)
            base_name = os.path.splitext(base_name)[0]
            urllib.request.urlretrieve(picture_url, "picture/" + base_name + ".jpg")
            jpg_file = os.path.join(os.getcwd(), "picture", base_name + ".jpg")
            print(jpg_file)
            mp3_file = base + ".mp3"

            video_file = moviepy.editor.AudioFileClip(downloadFile)
            video_file.write_audiofile(mp3_file)
            video_file.close()
            os.remove(downloadFile)

            qued_songs.append(mp3_file)
            qued_song_streams.append(currentVideo)
            qued_song_picture.append(jpg_file)
            if thread > 0:
                thread_avalibility[thread - 1] = True
            return
        except Exception as e:
            print(f"expetion occurd preparing: {e}")
    if thread > 0:
        thread_avalibility[thread - 1] = True
    print("Failed to prepapare music after multiple attempts")
    return

def play_next_song():
    global qued_song_streams, playingMusic, last_song, qued_song_picture, last_image, current_playing_song
    if len(qued_songs) > 0:
        imageHolder.configure(image=place_music_image)        
        try:
            current_playing_song.stop()
            os.remove(last_song)
            os.remove(last_image)
        except:
            print("No lst song")
        for i in range(len(qued_songs)):
            try:
                current_playing_song = vlc.MediaPlayer(qued_songs[i])
                break
            except Exception as e:
                print(e)
        current_playing_song.play()
        songName.configure(text=qued_song_streams[i].title)
        artist_name.configure(text=qued_song_streams[i].author)
        music_picture = CTk.CTkImage(dark_image=Image.open(qued_song_picture[i]),
                                     light_image=Image.open(qued_song_picture[i]),
                                     size=(100,100))
        imageHolder.configure(image=music_picture)
        last_song = qued_songs[i]
        last_image = qued_song_picture[i]
        qued_songs.pop(i)
        qued_song_streams.pop(i)
        qued_song_picture.pop(i)
        for k in range(i):
            qued_songs.pop(0)
            qued_song_picture.pop(0)
            qued_song_streams.pop(0)

    else:
        print("Next song is not ready yet, waiting...")
        return

def skipFuc():
    global playingMusic, ready_for_song
    if ready_for_song:
        ready_for_song = False
        skipButton.configure(text_color="red")
        song_thread = threading.Thread(target=songLoop)
        song_thread.start()    
    else:
        print("Can't skip right now, currently downloading new songs")

def clear_music_directory():
    try:
        for file in os.listdir(os.path.join(os.getcwd(), "music")):
            file_path = os.path.join(os.getcwd(), "music", file)
            os.remove(file_path)
    except:
        print("Could not clean entire music directory")
        
def clear_picture_directory():
    try:
        for file in os.listdir(os.path.join(os.getcwd(), "picture")):
            file_path = os.path.join(os.getcwd(), "picture", file)
            os.remove(file_path)
    except:
        print("Could not clean entire image directory")

def set_audio_volume(k):
    try:
        audio = sound_level.get()
        current_playing_song.audio_set_volume(audio)
    except Exception as e:
        print(e)
    return

def hide_name():
    songName.place_forget()
    artist_name.place_forget()
    imageHolder.place_forget()
    hideName.configure(text="Show name", command=show_name)
    return

def show_name():
    songName.place(relx=0.20,
               rely=0.88,
               anchor="w")
    artist_name.place(relx=0.20,
               rely=0.93,
               anchor="w")
    imageHolder.place(relx=0.10,
               rely=0.88,
               anchor="center")
    hideName.configure(text="Hide name", command=hide_name)
    return

def pause_music():
    current_playing_song.pause()
    stop_button.configure(text="Start music", command=start_music)

def start_music():
    global playingMusic
    current_playing_song.play()
    stop_button.configure(text="Stop music", command=pause_music)

def check_music_and_play():
    while True:
        try:
            print(current_playing_song.get_length() - current_playing_song.get_time())
            if current_playing_song.get_length() - current_playing_song.get_time() <= 1000:
                song_thread = threading.Thread(target=songLoop)
                song_thread.start()    
        except Exception as e:
            print(e)
        time.sleep(1)
        
root = CTk.CTk()
root.geometry("720x540")
root.title("Youtube Shuffler")
root.config(background="#0C0C0C")
root.resizable(width=True, height=True)

FONT = "Segoe UI Light"

play = CTk.StringVar()
playList = CTk.CTkEntry(root, textvariable=play,
                        width=350, height=10, bg_color="#0C0C0C",
                        fg_color="#141414", text_color="#0191DF",
                        border_color="#0C0C0C")
playList.place(relx=0.5,
               rely=0.05,
               anchor="center")

songName = CTk.CTkLabel(root, text="", font=(FONT, 25), bg_color="#0C0C0C",
                        fg_color="#0C0C0C", text_color="#0191DF"
)
songName.place(relx=0.20,
               rely=0.88,
               anchor="w")
artist_name = CTk.CTkLabel(root, text="", font=(FONT, 20), bg_color="#0C0C0C",
                        fg_color="#0C0C0C", text_color="#5B5B5B")
artist_name.place(relx=0.20,
               rely=0.93,
               anchor="w")
changePlay = CTk.CTkButton(root, text="Change Playlist", 
                           font=(FONT, 20), command=changePlaylist,
                           text_color="#5B5B5B", fg_color="#0C0C0C", bg_color="#0C0C0C")
changePlay.place(relx=0.5,
               rely=0.1,
               anchor="center")
    
skipButton = CTk.CTkButton(root, text="\U000025fc" + "Skip?", font=(FONT, 20),
                           width=10, 
                           command=skipFuc,bg_color="#0C0C0C",
                            fg_color="#0C0C0C", text_color="#0191DF")
skipButton.place(relx=0.80,
               rely=0.05,
               anchor="center")

stop_button = CTk.CTkButton(root, text="Stop song",font=(FONT, 20),
                            width=10, 
                           command=pause_music,bg_color="#0C0C0C",
                            fg_color="#0C0C0C", text_color="#0191DF")
stop_button.place(relx=0.5,
               rely=0.5,
               anchor="center")
sound_level = CTk.IntVar()
audioPanel = CTk.CTkSlider(root, from_=0, to=100, 
                       command=set_audio_volume, height=150, bg_color="#0C0C0C",
                       button_color="#0191DF", fg_color="#141414", progress_color="#2b2b2b",
                       orientation="vertical", variable=sound_level)
audioPanel.set(50)
audioPanel.place(relx=0.95,
               rely=0.9,
               anchor="s")

hideName = CTk.CTkButton(root, text="Hide name", command=hide_name,font=(FONT, 20),
                         width=20, text_color="#5B5B5B", bg_color="#0C0C0C",
                         fg_color="#0C0C0C")
hideName.place(relx=0.10,
               rely=0.05,
               anchor="center")

placeImage = "placeholders/placeholderimg.png"
place_music_image = CTk.CTkImage(dark_image=Image.open(placeImage),
                          light_image=Image.open(placeImage),
                          size=(100,100))

imageHolder = CTk.CTkButton(root, image=place_music_image,text="",
                            bg_color="#0C0C0C", fg_color="#0C0C0C",
                            text_color="#0C0C0C", hover=False)
imageHolder.place(relx=0.10,
               rely=0.88,
               anchor="center")
if not os.path.exists(os.getcwd() + r"\music"):
    os.makedirs(os.getcwd() + r"\music")
    
if not os.path.exists(os.getcwd() + r"\picture"):
    os.makedirs(os.getcwd() + r"\picture")
    
playingMusic = 0
current_song = None
qued_songs = []
qued_song_picture = []
qued_song_streams = []
last_song = ""
ready_for_song = True

song_thread = threading.Thread(target=songLoop)
check_song_ended = threading.Thread(target=check_music_and_play)
check_song_ended.start()

clear_music_directory()
clear_picture_directory()
root.mainloop()
