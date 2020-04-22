from sys import argv, stderr
from flask import Flask, request, redirect, make_response, url_for
from flask import render_template
from prof import Professor
from profsDB import profsDB
from CASClient import CASClient
from updateDB import updateDB, createProf
import psycopg2

app = Flask(__name__, template_folder='.')

# Generated by os.urandom(16)
app.secret_key = b'8\x04h\x0f\x08U0\xde\x1a\x92V\xe3\xd3\x9b5\xfa'

def getProfs(search_criteria, input_arguments):
    profsDB_ = profsDB()
    error_statement = profsDB_.connect()
    profs = []
    if error_statement == '':
        connection = profsDB_.conn
        try:
            if len(input_arguments) != 0:
                profs = profsDB_.displayProfessorsByFilter(connection, search_criteria, input_arguments)
            else:
                profs = profsDB_.displayAllProfessors(connection)
            profs = profsDB_.return_profs_list(profs)
        except Exception as e:
            error_statement = str(e)
    else:
        print(error_statement)
    return profs, error_statement

@app.route('/')
@app.route('/index')
def index():

    html = render_template('templates/index.html')
    response = make_response(html)
    return response

@app.route('/search')
def search():

    # username = CASClient().authenticate()

    html = render_template('templates/profs.html')
    response = make_response(html)
    return response

@app.route('/login')
def login():

    # username = CASClient().authenticate()
    
    html = render_template('templates/login.html')
    response = make_response(html)
    return response

@app.route('/logout', methods=['GET'])
def logout():
    
    # casClient = CASClient()
    # casClient.authenticate()
    # casClient.logout()

    html = render_template('templates/index.html')
    response = make_response(html)
    return response

@app.route('/button')
def button():

    # username = CASClient().authenticate()

    html = render_template('templates/search.html')
    response = make_response(html)
    return response

@app.route('/about')
def about():

    html = render_template('templates/about.html')
    response = make_response(html)
    return response

@app.route('/searchResults', methods=['GET'])
def searchResults():   

    # username = CASClient().authenticate()

    search_criteria, input_arguments = getSearchCriteria()

    profs, error_statement = getProfs(search_criteria, input_arguments)

    html = ''
    if error_statement == '':

        if len(profs) == 0:
            html += '<div class="no-search-results">' + \
                        '<h2>No search results. Please try use different keywords.</h2>' + \
                    '</div>'

        i = 0
        for prof in profs:
            html += '<div class="row">' + \
                        '<div class="prof-image">' + \
                            '<img src="' + prof[11] + '"/>' + \
                        '</div>' + \
                        '<div class="prof-info" onclick=' + '"collapse(' + str(i) + ')">' + \
                            '<p class="prof-name">' + prof[1] + ' ' + prof[2] + '</p>' + \
                            '<p class="prof-more-info">' + prof[3] + '</p>' + \
                            '<p class="prof-more-info">' + prof[8] + '</p>' + \
                            '<p class="prof-more-info">' + prof[5] + '</p>' + \
                            '<p class="prof-more-info">' + prof[7] + '</p>' + \
                            '<a href="mailto:' + prof[4] + '"><img class="icon" src="static/email-icon.png"></a>' + \
                            '<a href="' + prof[6] + '"><img class="icon" src="static/website-icon.png"></a>' + \
                        '</div>' + \
                        '<div class="button-div">' +\
                            '<button type="button" class="button" onclick=' + '"collapse(' + str(i) + ')"><img class="icon-button" id= img-' + str(i) + ' src="static/plus.png"></button>' + \
                        '</div>' + \
                    '</div>'+ \
                    '<div class="panel" id =panel-' + str(i) + '>' + \
                        '<div class="info-left">' + \
                            '<p class="sub-title"> Bio: </p>' + \
                            '<p class ="sub-info">' + prof[10] + '</p>' + \
                        '</div>' + \
                        '<div class="info-right">' + \
                            '<p class="sub-title"> Academic Interests: </p>' + \
                            '<p class ="sub-info">' + prof[9] + '</p>' + \
                        '</div>' + \
                    '</div>'
            i+=1
    else:
        html = render_template('templates/profs.html', error_statement=error_statement)
        print(error_statement, file=stderr)
    response = make_response(html)
    return response

def getSearchCriteria():
    input_arguments = []

    name = request.args.get('nameNetid')
    area = request.args.get('area')

    search_criteria = ''

    # search name/netid
    if name is None:
        name = ''
    name = name.strip()
    name = name.replace('%', r'\%')
    names = name.split()

    if len(names)==1:
        search_criteria += '(first' + ' ILIKE ' + '%s' + ' OR '
        search_criteria += 'last' + ' ILIKE ' + '%s' + ' OR '
        search_criteria += 'netid' + ' ILIKE ' + '%s)' + ' AND '
        input_arguments.append('%'+names[0]+'%')
        input_arguments.append('%'+names[0]+'%')
        input_arguments.append('%'+names[0]+'%')
    elif len(names) > 1:
        search_criteria += '((first' + ' ILIKE ' + '%s' + ' OR '
        search_criteria += 'last' + ' ILIKE ' + '%s' + ') AND '
        search_criteria += '(first' + ' ILIKE ' + '%s' + ' OR '
        search_criteria += 'last' + ' ILIKE ' + '%s))' + ' AND '
        input_arguments.append('%'+names[0]+'%')
        input_arguments.append('%'+names[0]+'%')
        input_arguments.append('%'+names[1]+'%')
        input_arguments.append('%'+names[1]+'%')

    # search research area/ bio
    if area is None:
        area = ''
    area = area.strip()
    area = area.replace('%', r'\%')
    areas = area.split(",")

    if len(areas) == 1:
        search_criteria += '(area' + ' ILIKE ' + '%s' + ' OR '
        input_arguments.append('%'+areas[0]+'%')
        search_criteria += 'bio' + ' ILIKE ' + '%s)' + ' AND '
        input_arguments.append('%'+areas[0]+'%')
    else:
        for i in range(len(areas)):
            search_criteria += '(area' + ' ILIKE ' + '%s' + ' OR '
            input_arguments.append('%'+areas[i]+'%')
            search_criteria += 'bio' + ' ILIKE ' + '%s)' + ' AND '
            input_arguments.append('%'+areas[i]+'%')

    if search_criteria != '' and search_criteria != None:
        search_criteria = search_criteria[:-5]
    return search_criteria, input_arguments


def getProfs(search_criteria, input_arguments):
    profsDB_ = profsDB()
    error_statement = profsDB_.connect()
    profs = []
    if error_statement == '':
        connection = profsDB_.conn
        try:
            if len(input_arguments) != 0:
                profs = profsDB_.displayProfessorsByFilter(connection, search_criteria, input_arguments)
            else:
                profs = profsDB_.displayAllProfessors(connection)
            profs = profsDB_.return_profs_list(profs)
        except Exception as e:
            error_statement = str(e)
    else:
        print(error_statement)
    return profs, error_statement


#----------------------------------------------------------------------------------------------------#
# Admin
#----------------------------------------------------------------------------------------------------#


@app.route('/admin', methods=["GET"])
def admin():
    html = render_template('index_tara.html')
    response = make_response(html)
    return response

@app.route('/profinfo', methods=["GET"])
def profinfo():
    netID = request.args.get('netid')
    prof, error_statement = getProfs('netid ILIKE %s', [netID])
    prof = prof[0]
    print(prof[1])

    if error_statement == '':
        if len(prof) == 0:
            html = \
                render_template('profinfo_tara.html', error_statement="No professor with netid '"
                 + netID + "' exists. Please try a different input")
        else:
            html = "<div class='profForm'>" + \
                        "<form>" + \
                            "<div class='form-group row'>" + \
                                "<label for='colFormLabel' class='col-sm-2 col-form-label'>NetID</label>" + \
                                "<div class='col-sm-10'>" + \
                                "<input type='text' class='form-control' id='colFormLabel' value='" + prof[0] + "'>" + \
                                "</div>" + \
                            "</div>" + \
                            "<div class='form-group row'>" + \
                                "<label for='colFormLabel' class='col-sm-2 col-form-label'>First Name</label>" + \
                                "<div class='col-sm-10'>" + \
                                "<input type='text' class='form-control' id='colFormLabel' value='" + prof[1] + "'>" + \
                                "</div>" + \
                            "</div>" + \
                            "<div class='form-group row'>" + \
                                "<label for='colFormLabel' class='col-sm-2 col-form-label'>Lat Name</label>" + \
                                "<div class='col-sm-10'>" + \
                                "<input type='text' class='form-control' id='colFormLabel' value='" + prof[2] + "'>" + \
                                "</div>" + \
                            "</div>" + \
                            "<div class='form-group row'>" + \
                                "<label for='colFormLabel' class='col-sm-2 col-form-label'>Title</label>" + \
                                "<div class='col-sm-10'>" + \
                                "<input type='text' class='form-control' id='colFormLabel' value='" + prof[3] + "'>" + \
                                "</div>" + \
                            "</div>" + \
                            "<div class='form-group row'>" + \
                                "<label for='colFormLabel' class='col-sm-2 col-form-label'>Email</label>" + \
                                "<div class='col-sm-10'>" + \
                                "<input type='text' class='form-control' id='colFormLabel' value='" + prof[4] + "'>" + \
                                "</div>" + \
                            "</div>" + \
                            "<div class='form-group row'>" + \
                                "<label for='colFormLabel' class='col-sm-2 col-form-label'>Phone Number</label>" + \
                                "<div class='col-sm-10'>" + \
                                "<input type='text' class='form-control' id='colFormLabel' value='" + prof[5] + "'>" + \
                                "</div>" + \
                            "</div>" + \
                            "<div class='form-group row'>" + \
                                "<label for='colFormLabel' class='col-sm-2 col-form-label'>Website</label>" + \
                                "<div class='col-sm-10'>" + \
                                "<input type='text' class='form-control' id='colFormLabel' value='" + prof[6] + "'>" + \
                                "</div>" + \
                            "</div>" + \
                            "<div class='form-group row'>" + \
                                "<label for='colFormLabel' class='col-sm-2 col-form-label'>Office</label>" + \
                                "<div class='col-sm-10'>" + \
                                "<input type='text' class='form-control' id='colFormLabel' value='" + prof[7] + "'>" + \
                                "</div>" + \
                            "</div>" + \
                            "<div class='form-group row'>" + \
                                "<label for='colFormLabel' class='col-sm-2 col-form-label'>Department</label>" + \
                                "<div class='col-sm-10'>" + \
                                "<input type='text' class='form-control' id='colFormLabel' value='" + prof[8] + "'>" + \
                                "</div>" + \
                            "</div>" + \
                            "<div class='form-group row'>" + \
                                "<label for='colFormLabel' class='col-sm-2 col-form-label'>Research Interests</label>" + \
                                "<div class='col-sm-10'>" + \
                                "<input type='text' class='form-control' id='colFormLabel' value='" + prof[9] + "'>" + \
                                "</div>" + \
                            "</div>" + \
                            "<div class='form-group row'>" + \
                                "<label for='colFormLabel' class='col-sm-2 col-form-label'>Bio</label>" + \
                                "<div class='col-sm-10'>" + \
                                "<textarea class='form-control' id='exampleFormControlTextarea1' rows='10'>" + prof[10] + "</textarea>" + \
                                "</div>" + \
                            "</div>" + \
                            "<div class='input-group mb-3'>" + \
                                "<label for='colFormLabel' class='col-sm-2 col-form-label'>Image</label>" + \
                                "<div class='custom-file'>" + \
                                    "<input type='file' class='custom-file-input' id='inputGroupFile02'>" + \
                                    "<label class='custom-file-label' for='inputGroupFile02' aria-describedby='inputGroupFileAddon02'>" + \
                                    prof[11] +\
                                    "</label>" + \
                                "</div>" + \
                                "<div class='input-group-append'>" + \
                                    "<span class='input-group-text' id='inputGroupFileAddon02'>Upload</span>" + \
                                "</div>" + \
                            "</div>" + \
                       "</form>" + \
                    "</div>" + \
                    """<form action="/displayprof" method="get">
                            <input class="searchButton overwriteButton" type="submit" name="button" id="overwriteProf" value="Save" onclick="overwriteProf()">
                        </form>
                        <form action="/admin"><input class="searchButton cancelOverwriteButton" type="submit" id="button" name="button" value="Cancel"></form>"""
    else:
        html = render_template('profinfo_tara.html', error_statement=error_statement)
        print(error_statement, file=stderr)
    response = make_response(html)
    response.set_cookie('netid', netID)
    return response

def newProf(netid):
    prof = Professor(netid)
    areas = request.args.get('areas')
    print(areas)
    prof.setTitle(request.args.get('title'))
    prof.setFirstName(request.args.get('firstname'))
    prof.setLastName(request.args.get('lastname'))
    prof.setEmail(request.args.get('email'))
    prof.setPhoneNumber(request.args.get('phone'))
    prof.setWebsite(request.args.get('website'))
    prof.setRooms(request.args.get('rooms'))
    prof.setDepartment(request.args.get('department'))
    prof.setResearchAreas(areas)
    prof.setBio(request.args.get('bio'))
    imagePath = "static\profImages\\" + netid + ".jpg"
    prof.setImagePath(imagePath)
    return prof

@app.route('/displayprof', methods=["GET"])
def displayprof():
    netID = request.cookies.get('netid')
    hostname = 'ec2-52-200-119-0.compute-1.amazonaws.com'
    username = 'hmqcdnegecbdgo'
    password = 'c51235a04a7593a9ec0c13821f495f259a68d2e1ab66a93df947ab2f31970009'
    database = 'd99tniu8rpcj0o'

    conn = psycopg2.connect( host=hostname, user=username, password=password, dbname=database)
    prof = newProf(netID)
    if request.args.get('button') == "Save":
        error_statement = updateDB(conn, prof)
    else: 
        error_statement = createProf(conn, prof)
    conn.close()
    if error_statement != '':
        print(error_statement)

    prof_, error_statement = getProfs('netid ILIKE %s', [netID])
    print(prof_[0])
    if error_statement == '':
        name = prof.getFirstName() + " " + prof.getLastName()
        html = \
            render_template('displayprof_tara.html', prof=prof_[0], name=name)
    else:
        html = render_template('displayprof_tara.html', error_statement=error_statement)
        print(error_statement, file=stderr)

    response = make_response(html)
    return response

if __name__ == '__main__':
    
    if (len(argv) != 2):
        print('Usage: ' + argv[0] + ' port', file=stderr)
        exit(1)

    try:
        port = int(argv[1])
    except:
        print("Port must be an integer", file=stderr)
        exit(1) 

    app.run(host='0.0.0.0', port=int(argv[1]), debug=True)
