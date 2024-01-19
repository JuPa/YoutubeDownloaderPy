import tkinter as tk
from tkinter import ttk
from pytube import Playlist, YouTube
from moviepy.editor import *
from urllib.parse import urlparse
from urllib.parse import parse_qs

"""

TODO: what about videos that contain &list=' in the url. technically this is a video in a playlist

https://www.youtube.com/watch?v=SelawmXHtPg&list=PL3JVwFmb_BnSOj_OtnKlsc2c7Jcs6boyB&index=1

https://www.youtube.com/playlist?list=PL3JVwFmb_BnSOj_OtnKlsc2c7Jcs6boyB

Either use import urlparse
or RegeXXXX

create a popup: "Playlist detected -> do you want to fetch the whole playlist?"
Yes _> extract link and paste it into current input
no -> just fetch Video

TODO: error handling for private playlists or videos
# i suppose i wont get a valid response... 

"""


class Downloader:
    window = None
    linkListContainer = None
    downloadType = None
    entryList = []
    message = None
    progressBar = None
    destroyCount = 0
    frame_id = None
    canvas  = None
    popupWindow = None
    errorMSG = ''
    def __init__(self):
        #https://www.youtube.com/playlist?list=PL3Qgpx2KozbJezBzfQ82jLiEeZwjEtejc
        self.window = window = tk.Tk()
        window.title("YouTube Downloader")
        window.geometry("600x400")
        window.minsize(600, 400)
        window.iconbitmap('themes/app.ico')
        
        container = ttk.Frame(self.window)
        self.canvas = canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)

        self.linkListContainer = scrollable_frame = ttk.Frame(canvas)
        scrollable_frame.pack(fill="x",side="right", expand=True)
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        self.frame_id = frameID = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw",width=380)#nw
        canvas.configure(yscrollcommand=scrollbar.set)
        container.pack(fill="both",expand=True,side="top", anchor='nw')
        canvas.pack(side="left", fill="both", expand=True,padx=5)
        scrollbar.pack(side="right", fill="y")
        #canvas.bind('<MouseWheel>', lambda event: canvas.yview_scroll(-int(event.delta / 60), "units"))
        canvas.bind('<MouseWheel>', lambda event: self.scroll_canvas(event))
        canvas.bind("<Configure>", self.resize_frame)
        scrollable_frame.bind('<MouseWheel>', lambda event: self.scroll_canvas(event))
        self.addLinkEntry()

        
        
        fetch_frame = ttk.Frame(master = window)
        self.downloadType = tk.StringVar()
        options = ["MP3", "MP4"]
        optionMenu = ttk.OptionMenu(fetch_frame, self.downloadType , "Select Type", *options)
        
        addButton = ttk.Button(master=fetch_frame, text="Add input", command=self.addLinkEntry)
        addButton.pack(side='left',padx=3)
        destroyButton = ttk.Button(master=fetch_frame, text="Clear All", command=self.destroy)
        destroyButton.pack(side='left',padx=3)
        fetchButton = ttk.Button(master=fetch_frame, text="Download", command=self.fetch)
        fetchButton.pack(side='left',padx=3)
        optionMenu.pack(side='left',padx=3)
        fetch_frame.pack(side='bottom', pady=(0,5))

        message_frame = ttk.Frame(master = window, height=40)

        self.message = tk.Message(master=message_frame,width=350)
        self.message.pack(side='top',expand=False, fill='y')
        self.progressBar = ttk.Progressbar(master=message_frame,length=350)
        self.progressBar.pack(side='bottom')
        self.progressBar.pack_forget()
        self.message.configure(text="Please insert any YouTubeLink into the link text field")
        message_frame.pack(side='bottom',expand=False, pady=(0,5))
        style = ttk.Style(window)
        self.window.tk.call('source','themes/azure/azure.tcl')
        self.window.tk.call('set_theme','light')#dark

        style.configure("success.TLabel", foreground="black", background="green")          
        style.configure("error.TLabel", foreground="black", background="red")
        window.mainloop()


    def scroll_canvas(self,event):
        """
        TODO
        Either make this dynamic and calc by what you can acutally see
        
        print(f"canvas {self.canvas.winfo_rootx()}, {self.canvas.winfo_rooty()}")

        print(f"entry {entry.winfo_rootx()}, {entry.winfo_rooty()}")

        or simply to the lazy aproach and assume if more than 4 [actual 5] liste ntrys are there we have to scroll
        """
        if ( len(self.entryList) > 4):           
            self.canvas.yview_scroll(-int(event.delta / 60), "units")

    def resize_frame(self, e):
        self.canvas.itemconfig(self.frame_id, width=(e.width-5))

    def addLinkEntry(self, videoLink=None):
        link = tk.StringVar()
        title = tk.StringVar()
        append = False
        if (videoLink == None):
            append = True

        link_frame = ttk.Frame(master = self.linkListContainer)
        link.trace_add('write',callback=lambda x, y, z, sv=link: self.callback(link, title, append))
        linkEntry = ttk.Entry(master=link_frame, textvariable=link)
        linkTitle = ttk.Entry(master=link_frame,textvariable=title)
        linkEntry.insert(0, 'Input a link')
        linkEntry.bind("<FocusIn>", lambda args: linkEntry.delete('0', 'end') if (linkEntry.get() == "Input a link") else '')
        deleteEntry = ttk.Button(master=link_frame, text="Delete", command= lambda: self.deleteEntry(link_frame))
        deleteEntry.pack(side='right',expand=False,fill='y',padx=(3,0))
        linkEntry.pack(expand=True, fill='x')
        linkTitle.pack(expand=True, fill='x')
        link_frame.pack(pady=(10,0),expand=True, fill='x')
        linkEntry.bind('<MouseWheel>', lambda event: self.scroll_canvas(event))
        linkTitle.bind('<MouseWheel>', lambda event: self.scroll_canvas(event))
        deleteEntry.bind('<MouseWheel>', lambda event: self.scroll_canvas(event))
        if (videoLink != None):
            link.set(videoLink)
        self.entryList.append(link_frame)

    def deleteEntry(self, link_frame):

        link_frame.pack_forget()
        if (link_frame.winfo_children()[0].get() == 'Input a link' and len(self.entryList) > 1):
            pass
        else:
            self.addLinkEntry()
        self.entryList.remove(link_frame)

    def fetch(self):
        self.message.configure(text="Starting download...")
        wrong = False
        fileType = self.downloadType.get() 
        if (fileType != "Select Type"):
            lenOfList = len(self.entryList)
            progress = tk.IntVar()
            self.progressBar.configure(maximum=lenOfList,variable=progress)
            progress.set(0)
            self.progressBar.pack()
            count = 0
            for element in self.entryList:
                children = element.winfo_children()
                if (len(children)>0):
                    link = children[0].get() # link
                    title = children[1].get()
                    if ((len(link)>0 and len(title)>0) or (self.videoOrPlaylist(link) != 1 and title != "Fetching Playlist...") or (len(title)>0)):
                        if (self.videoOrPlaylist(link) == 0):
                            #download video
                            title = self.cleanTitle(title)
                            response = False
                            if (fileType == "MP3"):
                                response = self.downloadFile(link, 0, title)
                            elif (fileType == "MP4"):
                                response= self.downloadFile(link, 1, title)
                            if (response == True):
                                children[0].configure(style="success.TLabel")
                                children[1].configure(style="success.TLabel")
                            else:
                                wrong = True
                                children[0].configure(style="error.TLabel")
                                children[1].configure(style="error.TLabel")
                        else:
                            wrong = True
                            children[0].configure(style="error.TLabel")
                            children[1].configure(style="error.TLabel")
                    elif (link != 'Input a link'):
                        children[0].configure(style="")
                        children[1].configure(style="")
                    else:
                        children[0].configure(style="")
                        children[1].configure(style="")
                        #link to short
                        pass
                count = count+1
                self.progressBar.step(count)
            if (wrong == False):
                self.message.configure(text="Download Complete!")
            else:
                self.message.configure(text="Please check wrong items. Errors: " +  self.errorMSG)
                self.errorMSG = ''
            progress.set(lenOfList)
        else:
            self.message.configure(text="Please select a filetype!")
            
    def cleanTitle(self,title):
        title = title.replace('\'',"").replace("/","").replace(":","").replace("*","").replace("?","").replace('"',"").replace('"',"").replace('<',"").replace('<',"").replace('|',"")
        return title

    def downloadFile(self, link, fileType, title):
        status = False
        v = YouTube(link)
        #basepath = os.path.dirname(os.path.realpath(__file__))
        #outputPath = os.path.join(basepath,"output")
        try:
            os.mkdir("/output")
        except:
            pass
        try:
            if (fileType == 0):# mp3
                v.streams.get_audio_only().download(output_path="output", filename=(title+'.mp3'))
                status = True
            elif (fileType == 1): #mp4
                v.streams.get_highest_resolution().download(output_path="output", filename=(title+'.mp4'))
                status = True
            else:
                status = False
                #wrong filetype
                pass
        except Exception as e:
            #print(str(e))
            self.errorMSG = self.errorMSG + f' {str(e)}'
            status = False
        finally:
            return status

    def videoOrPlaylist(self, str):
        if "watch" in str:
            if ("&list=" in str):
                return 2
            return 0
        elif "playlist" in str:
            return 1
        else:
            return None

    def callback(self, linkVar, titleBar, append, presetLink = None):
        #print(f"callback from {linkVar} {titleBar} append: {append} linK {presetLink}")
        if (presetLink != None):
            linkVar.set(presetLink)
        link = linkVar.get()
        if(self.videoOrPlaylist(link) == 0):
                    #video, so append titlefield
                    titleBar.set(self.getVideoTitle(link))
                    #if video title added, add a new row to insert line
        elif(self.videoOrPlaylist(link) == 1):
            #fetch all entries
            videos = self.getPlaylistVideos(link)
            if (titleBar.get() != "Fetching Playlist..."): # check if already fetched to prevent double loading.... can cause some issues
                if ( len(videos)>0):
                    titleBar.set("Fetching Playlist...")
                    for video in videos:
                        self.addLinkEntry(video)
                else:
                    titleBar.set("Error fetching Playlist, private link?")
                append = True
            else:
                append = False
        elif(self.videoOrPlaylist(link) == 2):
            append = False
            #fetch all entries
            #https://www.youtube.com/watch?v=SelawmXHtPg&list=PL3JVwFmb_BnSOj_OtnKlsc2c7Jcs6boyB&index=1
            parsed_url = urlparse(link)
            listParam = parse_qs(parsed_url.query)['list'][0]
            watchParam = parse_qs(parsed_url.query)['v'][0]
            videoLink = f"https://www.youtube.com/watch?v={watchParam}"
            playlistLink = f"https://www.youtube.com/playlist?list={listParam}"
            #linkVar.set()
            """
            Create Popup
            TODO rework this___            
            """
            self.popupWindow = tk.Toplevel(self.window)
            self.popupWindow.iconbitmap('themes/app.ico')
            #style = ttk.Style(self.popupWindow)
            #self.popupWindow.tk.call('source','themes/azure/azure.tcl')
            
            label = tk.Label(self.popupWindow, text="Video in playlist detected, do you \nwant to fetch the whole playlist?")
            label.pack(fill='x', padx=50, pady=5)
            button_yes = tk.Button(self.popupWindow, text="Yes", width=5, command=lambda: [self.popupWindow.destroy(), self.callback(linkVar, titleBar, False, playlistLink)])
            button_yes.pack(fill='x',side="left",pady=10, padx=15)
            button_no = tk.Button(self.popupWindow, text="No", width=5, command=lambda: [self.callback(linkVar, titleBar, False, videoLink), self.popupWindow.destroy()])
            button_no.pack(fill='x',side="right",pady=10, padx=15)
            #TODO fix styling for popup
            self.popupWindow.tk.call('set_theme','light')#dark
        else:
            if (link == 'Input a link' or link == ''):
                titleBar.set("")
            else:
                titleBar.set("Not a valid Link")
            #TODO add message for private playlist/video
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
            titles.append("Error fetching Title, wrong/broken or private link?")
        finally:
            return titles

    def getVideoTitle(self,link):
        title = ""
        try:
            v = YouTube(link)
            title = v.title
        except:
            title = "Error fetching Title, wrong/broken or private link?"
        finally:
            return title

    def destroy(self):
        if (self.destroyCount == 0):
            self.message.configure(text="Please press again to clear all entrys")
            self.destroyCount+=1
        else:
            for entry in self.entryList:
                entry.pack_forget()
            if (self.progressBar != None):
                self.progressBar.pack_forget()
            self.entryList.clear()
            self.addLinkEntry()
            self.message.configure(text="Please insert any YouTubeLink into the link text field")      
    
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
