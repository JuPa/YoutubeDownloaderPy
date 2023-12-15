import tkinter as tk
from tkinter import ttk
from pytube import Playlist, YouTube
from moviepy.editor import *

class Downloader:
    window = None
    linkListContainer = None
    downloadType = None
    entryList = []
    message = None
    progressBar = None
    destroyCount = 0
    def __init__(self):
        self.window = window = tk.Tk()
        window.title("YouTube Downloader")
        window.geometry("600x400")

        self.linkListContainer = video_frame = ttk.Frame(master = window)
        self.addLinkEntry()
        video_frame.pack(side='top',expand=False, fill='x', padx=10)

        fetch_frame = ttk.Frame(master = window)
        self.downloadType = tk.StringVar(value="Select Type")
        w = ttk.OptionMenu(fetch_frame, self.downloadType ,"MP3", "MP4") 
        fetchButton = ttk.Button(master=fetch_frame, text="Download", command=self.fetch)
        fetchButton.pack(side='left')
        destroyButton = ttk.Button(master=fetch_frame, text="Clear All", command=self.destroy)
        destroyButton.pack(side='left')
        w.pack(side='left')
        fetch_frame.pack(side='bottom', pady=(0,5))

        message_frame = ttk.Frame(master = window, height=40)

        self.message = tk.Message(master=message_frame,width=350)
        self.message.pack(side='top',expand=False, fill='y')
        self.progressBar = ttk.Progressbar(master=message_frame,length=350)
        self.progressBar.pack(side='bottom')
        self.progressBar.pack_forget()
        self.message.configure(text="Please insert any YouTubeLink into the link text field")
        message_frame.pack(side='bottom',expand=False, pady=(0,5))
        window.mainloop()

    def addLinkEntry(self, videoLink=None):
        link = tk.StringVar()
        title = tk.StringVar()
        append = False
        if (videoLink == None):
            append = True
        link.trace_add('write',callback=lambda x, y, z, sv=link: self.callback(link, title, append))
        linkEntry = ttk.Entry(master=self.linkListContainer, textvariable=link)
        linkTitle = ttk.Entry(master=self.linkListContainer,textvariable=title)
        deleteEntry = ttk.Button(master=self.linkListContainer, text="Delete", command= lambda: self.deleteEntry(linkEntry, linkTitle, deleteEntry))
        deleteEntry.pack(side='right',expand=False,fill='y',pady=(10,0))
        linkEntry.pack(expand=True, fill='x', pady=(10,0))
        linkTitle.pack(expand=True, fill='x')
        if (videoLink != None):
            link.set(videoLink)
        self.entryList.append([linkEntry,linkTitle, deleteEntry])

    def deleteEntry(self, linkEntry, linkTitle, deleteEntry):
        deleteEntry.pack_forget()
        linkEntry.pack_forget()
        linkTitle.pack_forget()
        self.entryList.remove([linkEntry,linkTitle, deleteEntry])
        self.addLinkEntry()

    def fetch(self):
        wrong = False
        filyType = self.downloadType.get() 
        if (filyType != "Select Type"):
            lenOfList = len(self.entryList)
            self.message.configure(text=f"Starting download of {lenOfList-1} items...")
            progress = tk.IntVar()
            self.progressBar.configure(maximum=lenOfList,variable=progress)
            progress.set(0)
            self.progressBar.pack()
            count = 0
            for element in self.entryList:
                link = element[0].get() # link
                title = element[1].get()
                if (self.videoOrPlaylist(link) == 0):
                    #download video
                    if (filyType == "MP3"):
                        self.downloadFile(link, 0, title)
                    if (filyType == "MP4"):
                        self.downloadFile(link, 1, title)
                    style = ttk.Style()
                    style.configure("BW.TLabel", foreground="black", background="green")
                    element[0].configure(style="BW.TLabel")
                    element[1].configure(style="BW.TLabel")
                else:
                    wrong = True
                    style = ttk.Style()
                    style.configure("BW.TLabel", foreground="black", background="red")
                    element[0].configure(style="BW.TLabel")
                    element[1].configure(style="BW.TLabel")
                count = count+1
                self.progressBar.step(count)
            
            if (wrong == False):
                self.message.configure(text="Download Complete!")
            else:
                self.message.configure(text="Please check wrong items")
            progress.set(lenOfList)
        else:
            self.message.configure(text="Please select a filetype!")
            

    def downloadFile(self,link,fileType, title):
        v = YouTube(link)
        basepath = os.path.dirname(os.path.realpath(__file__))
        outputPath = os.path.join(basepath,"output")
        try:
            os.mkdir(outputPath)
        except:
            pass
        if (fileType == 0):# mp3
            v.streams.get_audio_only().download(output_path=str(outputPath), filename=(title+'.mp3'))
        if (fileType == 1): #mp4
            v.streams.get_highest_resolution().download(output_path=str(outputPath), filename=(title+'.mp4'))
        else:
            print("Wrong filetype")


    def videoOrPlaylist(self, str):
        if "watch" in str:
            return 0
        elif "playlist" in str:
            return 1
        else:
            return None

    def callback(self, linkVar, titleBar, append):
        link = linkVar.get()
        if(self.videoOrPlaylist(link) == 0):
            #video, so append titlefield
            titleBar.set(self.getVideoTitle(link))
            #if video title added, add a new row to insert line

        elif(self.videoOrPlaylist(link) == 1):
            #fetch all entries
            videos = self.getPlaylistVideos(link)
            for video in videos:
                self.addLinkEntry(video)
        else:
            titleBar.set("Not a valid Link")
            append = False
        if (append):
            self.addLinkEntry()

    def getPlaylistVideos(self,playlistLink):
        titles = []
        try:
            v = Playlist(playlistLink)
            for video in v.videos:
                titles.append(video.watch_url)
        except:
            titles.append("Error fetching Title, wrong or broken link?")
        finally:
            return titles

    def getVideoTitle(self,link):
        title = ""
        try:
            v = YouTube(link)
            title = v.title
        except:
            title = "Error fetching Title, wrong or broken link?"
        finally:
            return title

    def destroy(self):
        if (self.destroyCount == 0):
            self.message.configure(text="Please press again to clear all entrys")
            self.destroyCount+=1
        else:
            for entry in self.entryList:
                entry[0].pack_forget()
                entry[1].pack_forget()
                entry[2].pack_forget()
            self.entryList.clear()
            self.addLinkEntry()
            #window = self.window
            #window.destroy()
            #self.__init__()
        
    
def main():
    d = Downloader()

if __name__ == "__main__":
    main()





"""
#https://www.youtube.com/playlist?list=PLIO3v6wq4-OjP06J-_rAzq7dJIanKTxDI
https://www.youtube.com/watch?v=VRwxgYzRTBI

have link to pass, either input playlist or watch link. (detect with regex)
If playlist passed automatically extract every song...

GUI:

LINKInput
TitleEditfield


fileformat (mp4/mp3), Fetch Button

"""
