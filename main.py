from flask import Flask, render_template, request, send_file
import os
import requests
from bs4 import BeautifulSoup
from lxml import html
import re
import emotRecog as er
app = Flask(__name__,template_folder='html')

@app.route('/')
def home():
    return render_template('index.html')

@app.route("/get_top_songs", methods=["POST"])
def get_top_songs():
    try:

        artist_name = request.form["artist_name"]
        goodformat = artist_name.lower()
        url = "https://genius.com/artists/" + goodformat.replace(" ", "-")
        
        response = requests.get(url)
        tree = html.fromstring(response.content)
        song_titles = tree.xpath('//div[@class="mini_card-title"]/text()')[:5]
        #
        
        song_links = tree.xpath('//a[@class="mini_card"]/@href')[:5]
        # print the href
        print(song_links)
        
        # Extract the song thumbnails
        thumbnails = tree.xpath('//div[contains(@class, "mini_card-thumbnail")]/@style')
        thumbnails = [re.search(r'url\((.*?)\)', t).group(1) for t in thumbnails]
        


    # Print the URLs of the song thumbnails
        
        cards = ""
        for i in range(5):
            song_title = song_titles[i]
            thumbnail = thumbnails[i]
            index=i+1
            song_link = song_links[i]
            song_link_clean = song_link.strip()
            ##remove the whitespaces from the song title
            
            
            song_title_clean = song_title.strip()
            #remove ppunctuation from the song title using regex
            song_title_clean = re.sub(r'[^\w\s]','',song_title_clean)

            
            
            cards += f"""<div class="card" value="{index}" >
                <div class="card-img" style="background-image:url({thumbnail});" alt="Card image cap"></div>
                <div class="card-body">
                    <h5 class="card-title">{song_title}</h5>
                    <input type="button" class="lyricBut" value="Lyrics" onclick="get_lyrics('{song_title_clean}','{artist_name}','{song_link_clean}')">
                </div>
            </div>"""
            
        
        return f'<h2>Results for {artist_name}:</h2><div class="card-deck">{cards}</div>'
    except:
        return f'<h2>Results for {artist_name}:</h2><div class="card-deck"><div class="errorCard"><h1>Sorry, we couldn\'t find any songs for this artist.</h1></div></div>'

@app.route("/get_lyrics", methods=["POST"])
def get_lyrics():
    try:
        song_title = request.form["song_name"]
        artist_name = request.form["artist_name"]
        song_link = request.form["lyrics_link"]
        print(song_link)
        response = requests.get(song_link)
        soup = BeautifulSoup(response.text, "html.parser")
        elem = soup.find("div", class_="PageGriddesktop-a6v82w-0 SongPageGriddesktop-sc-1px5b71-0 Lyrics__Root-sc-1ynbvzw-0 iEyyHq").find_all("div", class_="Lyrics__Container-sc-1ynbvzw-5 Dzxov")
        lyrics = ""
        for div in elem:
            elem = div.get_text(separator="<br>")
            lyrics += elem
        
        lyrics = re.sub(r'\]', r']<br>', lyrics)
        lyrics = re.sub(r'\[', r'<br><br>[', lyrics)
        
        
        
        newlyrics = re.sub(r'\[.*?\]', '', lyrics)
        #change all the <br> to new line
        newlyrics = newlyrics.replace("<br>", "\n")
        
        emotions=er.analyze_lyric(newlyrics)
        divString = f'<div id="emotions">'

        for emotion in emotions:
            # give the highest value a different color
            if emotions[emotion] == max(emotions.values()):
                divString += f'<h4 id="highest">{emotion} {round(emotions[emotion]*100,1)}%</h4>'
            else:
                divString += f'<h4>{emotion} {round(emotions[emotion]*100,1)}%</h4>'
        divString += f'</div>'
        # create another string to store the emotions as text for the download button
        emotionString = f''
        for emotion in emotions:
            emotionString += f'{emotion} {round(emotions[emotion]*100,1)}%,'
        emotionString = emotionString[:-1]
        
        
        

        return f"""<h2>Lyrics for {song_title} by {artist_name}:</h2><div class="card-deck-lyrics"><div class="analyzeContainer"><input type="button" id="analyzeBut" value="Analyze" onclick="changeContCss()">{divString}</div><div class="card-lyrics"><h4>{lyrics}</h4></div><input type="button" id="downBut" value="Download Lyrics And Emotions" onclick="save_LyricsEmotion('{emotionString}','{song_title}','{artist_name}')"></div></div>"""
    except Exception as e:
        print(e)
        return f'<h2>Results for {artist_name}:</h2><div class="card-deck"><div class="errorCard"><h1>Sorry, we couldn\'t find any Lyrics for this song.</h1></div></div>'

@app.route("/save_LyricsEmotion", methods=["POST"])
def save_LyricsEmotion():
    
    song_title = request.form["song_title"]
    lyrics = request.form["lyrics"]
    emotions = request.form["emotion"]
    artist_name = request.form["artist_name"]
    
    lyrics = lyrics.replace("<br>", "\n")
    #clean the lyrics from the h tags
    lyrics = re.sub(r'<h4>', '', lyrics)
    lyrics = re.sub(r'</h4>', '', lyrics)
    
    song_title = re.sub(r'[^\w\s]','',song_title)
    song_title = song_title.replace(" ", "_")
    
    artist_name = re.sub(r'[^\w\s]','',artist_name)
    artist_name = artist_name.replace(" ", "_")


    #create a new file with the song title as the name
    file_name = f'{song_title}-LyricsAndEmotions.txt'
    file_path = f'{song_title}-LyricsAndEmotions.txt'
    with open(file_path, 'w') as file:
        #write the lyrics and emotions to the file
        file.write(f'Lyrics for {song_title} by {artist_name}\n\n {lyrics}\n\nEmotions:\n\n{emotions}')
    # send file name
    return file_name
@app.route("/download_file", methods=["POST"])
def download_file():
    file_name = request.form["file_name"]
    return send_file(file_name, mimetype='text/plain', as_attachment=True)
@app.route('/delete_file', methods=['POST'])
def delete_file():
    file_name = request.form['file_name']
    os.remove(file_name)
    return 'File deleted successfully!'    
    

if __name__ == '__main__':
    app.run(debug=True)
