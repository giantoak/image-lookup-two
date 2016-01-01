A Flask app for conducting reverse image search using Google's API.

Sample usage:
1. `conda create --name image-lookup --file requirements.txt` to create the program environment
1. `source activate image-lookup` to enter the environment
1. `python run.py` to start the server.
1. In a second terminal, start running [ngrok](https://ngrok.com/) (`ngrok http 8080`) or your 
html-interface-exposing tool of choice. Alternately, run the program as a dedicated web app on a specific web server.
1. Go to [0.0.0.0:8080](http://0.0.0.0:8080) - or your publicly exposed http endpoint- in your browser of 
choice. (It should be a *recent* browser, given [Flask-SocketIO's](https://flask-socketio.readthedocs.org/en/latest/) constraints.)
1. Use the file browser to upload an image.
1. Browse the gallery of results



Notes on interacting with Google Reverse Image Search (as of December, 2015)
1. There are two ways to access image search:
  * Send a link to a hoosted version at the end of the query: `http://images.google
  .com/searchbyimage?image_url=[image url]`
  * send a copy of the image to google directly: `http://www.google.com/searchbyimage/upload` with an `encoded_image`
   field containing the raw image data and an `image_content` field containing an empty string.
1. Either way, before connecting to search you *must* create a User-Agent header for a modern browser.
1. Google will respond with a redirect to a results page (in a `Location` field).
1. This page will include results, *plus* a tag linking to a much larger, "visually similar images" results page: `<a 
href="[url]">Visually similar images</a>`. Extract this tag, and request the linked page.
1. This final page will contain a number of results for us to extract, generally conforming to the [schema.org's Search 
Results Page standard](https://schema.org/SearchResultsPage):
  * `<a class="qb-b">[query text]</a>`, if google has a search query associated with this particular image. (This 
  isn't likely, unless we're searching on something particularly popular.
  * All results are nested within tags of the form `<div class="rg_di rg_el ivg-i">` Of particular note within are 
  these three tags:
    * `<a class="rg_l" href="/imgres?imgurl=[url of image]&amp;imgrefurl=[website of image]&amp;
    h=[height]&w=[width]&amp;tbnid=[google internal id]&amp;…&amp;…" …>`
    * `<span class="rg_ilmn">[resolution] - [image domain]</span>`
    * `<div class="rg_meta">{JSON dict of various features}</div>`
      * `pt`: Some type of heading or subject string. I'm uncertain if this key is mandatory.
      * `s`: An additional subject string. It may or may not be the same as `pt`. I'm uncertain if this key is 
      mandatory.
      * `id`: A repeat of the `tbnid` value mentioned above.
  * This is *brittle*, but within the eight `<script>` tag google stores thumbnails of the first ten images, keyed 
  with the `tbnid` value. If you can get to the right portion, you can extract the raw image.