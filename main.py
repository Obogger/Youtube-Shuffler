import pytube
#import webbrowser
import random
import time
import tkinter as tk
import os
import pygame
import moviepy.editor
import glob
import threading

#Accesability
#Skipknapp

def changePlaylist():
    global p
    p = pytube.Playlist(play.get())
    play.set("")
    
def songLoop():
    global qued_songs
    prepare_next_song_thread_first = threading.Thread(target=prepare_next_song)
    prepare_next_song_thread_second = threading.Thread(target=prepare_next_song)
    if(len(qued_songs) > 0):
        prepare_next_song_thread_first.start()
    else:
        prepare_next_song()
    play_next_song()
    if(len(qued_songs)  < 3):
        prepare_next_song_thread_second.start()
        print("Dubble buffering")
    while prepare_next_song_thread_first.is_alive() or prepare_next_song_thread_second.is_alive():
        time.sleep(1)
    skipButton.config(background="Green")
    return
    
    
    return
        
def prepare_next_song():   
    global qued_songs 
    for _ in range(5):
        try:
            url = random.choice(p)
            currentVideo = pytube.YouTube(url)
            
            audio_stream = currentVideo.streams.get_audio_only()
            downloadFile = audio_stream.download(output_path=os.path.join(os.getcwd(), "music"))
            
            base, ext = os.path.splitext(downloadFile)
            mp3_file = base + ".mp3"

            video_file = moviepy.editor.AudioFileClip(downloadFile)
            video_file.write_audiofile(mp3_file)
            video_file.close()
            os.remove(downloadFile)

            qued_songs.append(mp3_file)
            qued_song_streams.append(currentVideo) 
            return
        except Exception as e:
            print(f"expetion occurd preparing: {e}")
            
    print("Failed to prepapare music after multiple attempts")
    return

def play_next_song():
    global qued_songs, qued_song_streams, playingMusic, last_song
    if len(qued_songs) > 0:
        pygame.mixer.music.unload()
        try:
            os.remove(last_song)
        except:
            print("No lst song")
        for i in range(len(qued_songs)):
            try:
                pygame.mixer.music.load(qued_songs[i])
                break
            except Exception as e:
                print(e)
        pygame.mixer.music.play(loops=0)
        songName.config(text=qued_song_streams[0].title)
        playingMusic = root.after(int(qued_song_streams[0].length * 1000), songLoop)
        last_song = qued_songs[i]
        qued_songs.pop(i)
        qued_song_streams.pop(i)
    else:
        print("Next song is not ready yet, waiting...")
        return
def skipFuc():
    global playingMusic, song_thread
    try:
        root.after_cancel(playingMusic)
    except:
        print("Noting to chancel")
        
    if not song_thread.is_alive():
        skipButton.configure(background="Red")
        song_thread = threading.Thread(target=songLoop)
        song_thread.start()    
    else:
        print("Currently skipping and downloading")


def clear_music_directory():
    try:
        for file in os.listdir(os.path.join(os.getcwd(), "music")):
            file_path = os.path.join(os.getcwd(), "music", file)
            os.remove(file_path)
    except:
        print("could not clea all")

    
root = tk.Tk()
root.geometry("500x500")
root.title("Player")

pygame.mixer.init()

play = tk.StringVar()
playList = tk.Entry(root, textvariable=play)
playList.place(relx=0.5,
               rely=0.1,
               anchor="center")

songName = tk.Label(root, text="", font=('Arial', 20))
songName.place(relx=0.5,
               rely=0.5,
               anchor="center")
changePlay = tk.Button(root, text="Change palylist?!?!", font=('Arial', 10), command=changePlaylist)
changePlay.place(relx=0.5,
               rely=0.15,
               anchor="center")
    
skipButton = tk.Button(root, text="Skip", font=('Arial', 20), command=skipFuc, background="Green")
skipButton.place(relx=0.75,
               rely=0.75,
               anchor="center")

if not os.path.exists(os.getcwd() + r"\music"):
    os.makedirs(os.getcwd() + r"\music")

playingMusic = 0
current_song = None
qued_songs = []
qued_song_streams = []
last_song = ""

song_thread = threading.Thread(target=songLoop)

pygame.mixer.init()

clear_music_directory()

root.mainloop()
