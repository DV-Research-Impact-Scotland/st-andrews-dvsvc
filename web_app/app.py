from flask import Flask, request, render_template, redirect, url_for, session
import queries
from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import geopy.distance
UK_LENGTH = 1000
USER_AGENT = "DASAD/0.1"
DELAY = 1
PAGE_LIMIT = 10
app = Flask(__name__)
geolocator = Nominatim(user_agent=USER_AGENT)
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=DELAY)


"""
Retrieves coordinates of a given string location/postcode
"""
@app.route("/convert/<location>", methods = ["GET"])
def get_coordinates(location: str):
    try:
      conv = geocode(f"{location}, UK", exactly_one=True)
      if conv is not None:
         return [conv.address, conv.latitude, conv.longitude]
      return [None, None, None]
    except Exception as e:
      print(f"Error: {e}")
      return [None, None, None]

"""
Takes in postcode and distance from form, and obtains list of charities in that distance, or nearest reasonable distance
"""
@app.route("/", methods = ['POST', 'GET'])
def location_filter():
    if request.method == "POST":
        current_loc = request.form["loc"]
        current_dist = int(request.form["dist"])
        original_dist = current_dist
        address, lat, long = get_coordinates(current_loc)
        if address is None:
            nearby = []
        else:
            nearby = queries.get_locations(lat, long, int(current_dist))
            # expand until either item found or length of UK covered 
            while nearby == [] and current_dist < UK_LENGTH:
                nearby = queries.get_locations(lat, long, int(current_dist))
                current_dist = current_dist + 50
        
        # distance should be 1000 or not a location, so just search for all UK charities. Paginate search
        if nearby == []:
           return redirect(url_for("all_charity_list",location = current_loc, distance=original_dist, page=1))
        else:
           return redirect(url_for("search_charity_list",location = current_loc, distance=original_dist, current_dist = current_dist, page=1))

    return render_template("index.html", loc="Postcode", dist="distance")


""" Paginates all uk search. Access separately, or through search"""
@app.route("/all/<page>")
@app.route("/all/<location>/<distance>/<page>")
def all_charity_list(page, location="location", distance="distance", current_dist=0): #current_dist to match search_charity_list
    # Have to requery database for each page - see if can avoid this, consider using cookies or session?
    charity_list = queries.get_all_charities()
    outstr = f"""<p>Could not find Location. All charities in database</p> <ul class='result'>"""
    page = int(page)
    # list all charities within given range for that page, calculated from current length and the page limit (number of charities per page)
    for c in charity_list[(page-1)*PAGE_LIMIT: (page)*PAGE_LIMIT]:
        outstr = outstr + f"""<li onclick="location.href='{url_for('charity_page',index=c[0])}';", class="card"><div >
        <h3>{c[1]}</h3>
        <a href='{c[2]}'> {c[2]} </a>
        <br>
        <br>
        {c[3]}
        <br>

        </div></li>"""

    outstr += "</ul>"

    # build page navigation 
    num_pages = int(len(charity_list)/PAGE_LIMIT)
    if (len(charity_list) % PAGE_LIMIT != 0):
        num_pages += 1
    outstr = outstr + page_links(num_pages, page, "all_charity_list", location, distance, current_dist)
    return render_template("index.html", result=outstr, loc=location, dist=distance)

""" Paginates search result for location and distance"""
@app.route("/<location>/<distance>/<current_dist>/<page>")
def search_charity_list(page, location, distance, current_dist):
    address, lat, long = get_coordinates(location)
    # As in all_charity_list, have to requery database each time - limit to only values needed?
    if address is None:
        charity_list = []
    else:
        charity_list = queries.get_locations(lat, long, int(current_dist))
    outstr = f""" {'<p>All charities with UK locations</p>' if int(current_dist) > UK_LENGTH else '<p>All charities within ' + str(current_dist) + ' km of ' + address + '</p>'}<ul class='result'>"""  

    page = int(page)
    # list all charities within given range for that page, calculated from current length and the page limit (number of charities per page)
    for c in charity_list[(page-1)*PAGE_LIMIT: (page)*PAGE_LIMIT]:
        outstr = outstr + f"""<li onclick="location.href='{url_for('charity_page',index=c[0])}';", class="card"><div >
                <h3>{c[1]}</h3>
                <a href='{c[3]}'> {c[3]} </a>
                <br>
                <br>
                {c[2]}, {(c[5]/1000):.2f}km away
                <br>
                <br>
                {c[4]}
                <br>

                </div></li>"""

    outstr += "</ul>"
    # build page navigation 
    num_pages = int(len(charity_list)/PAGE_LIMIT)
    if (len(charity_list) % PAGE_LIMIT != 0):
        num_pages += 1
    outstr = outstr + page_links(num_pages, page, "search_charity_list", location, distance, current_dist)
    return render_template("index.html", result=outstr, loc=location, dist=distance)

"""
Page navigation at bottom of page, each button links to that number page
"""
def page_links(num_pages, curr_page, redirect, location, distance, current_dist):
    out = "<div> <ul class='pagination'>"
    for i in range(1, num_pages+1):
        if i == curr_page:
            out = out + f"""<li><u>{i}</u></li>"""
        else:
            out = out + f"""<li><a href={url_for(redirect, page=i, location=location, distance=distance, current_dist=current_dist)}>{i}</a></li>"""
    out += "</ul> </div>"
    return out


"""
Information about charity with that index number displayed in own page
"""
@app.route("/charity/<index>")
def charity_page(index):
    # link in stylesheet - currently builds from scratch here, use template instead?
    page = f"""<head><link rel="stylesheet" href="{ url_for('static', filename='index.css') }">
</head>
<body> 
"""
    # get and display information about charity in general.
    charity_info = queries.get_charity_info_by_id(index)
    if charity_info == []:
        return "<h1>Unknown Charity</h1>"
    charity_info = charity_info[0]
    charity_details = f"""
    <h1>{charity_info[3]}</h1>
    <div>
        <a href='{charity_info[0]}'> {charity_info[0]} </a>
        <br>
        <br>
        {charity_info[1]}
        <br>
        <br>
        Charity Number: {charity_info[2]}
    </div>
    """
    # Get and display information about each service charity provides
    service_info = queries.get_all_service_info_by_charity_id(index)
    service_details = "<h2>Services</h2><ul class=result>"
    for s in service_info:
        service_details = service_details + f"""
                <li>
                <div class="card">
                    {s[1]}
                    <br>
                    <br>
                    {",".join(s[4])}
                    <br>
                    {",".join(s[2])}
                    <br>
                    {",".join(s[3])}
                    <br>
                    <br>
                </div>
                <br>
                </li>
        """
    page = page + charity_details + service_details+"</ul> </body>"
    return page

""" Show map view """
@app.route("/map", methods = ['POST', 'GET'])
def map_view():
    return render_template("map.html")

"""Returns list of all charitys for map view"""
@app.route("/mapApi/all",  methods = ['GET'])
def get_all_charity_info():
    return list(map(lambda x: {"charity_id": x[0], "charity_name": x[1], "location_name": x[2], "latitude": x[3], "longitude": x[4], "url": x[5], "summary": x[6]},  queries.get_all_locations()))

"""Returns list of charities within search radius from form"""
@app.route("/mapApi/loc", methods = ['POST', 'GET'])
def get_filtered_locations():
    if request.method == "POST":
        current_loc = request.form["loc"]
        current_dist = int(request.form["dist"])
        original_dist = current_dist
        address, lat, long = get_coordinates(current_loc)
        if address is None:
            nearby = []
        else:
            nearby = queries.get_locations(lat, long, int(current_dist))
            # expand until either item found or length of UK covered 
            while nearby == [] and current_dist < UK_LENGTH:
                nearby = queries.get_locations(lat, long, int(current_dist))
                current_dist = current_dist + 50
        
        return list(map(lambda x: {"charity_id": x[0], "charity_name": x[1], "location_name": x[2],  "url": x[3], "summary": x[4], "distance": x[5], "latitude": x[6], "longitude": x[7]},  nearby))
