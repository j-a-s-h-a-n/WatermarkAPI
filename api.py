from flask import Flask, request,jsonify,send_file
from flask_restful import Resource, Api, reqparse
from PIL import Image, ImageDraw, ImageFont
import os

app = Flask(__name__)
api = Api(app)

UPLOAD_FOLDER = '/images'
download_path  = '/watermarked.jpg'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

watermarks=[]
fontz = []
position = []

fonts = {
    'arial':'Arial Italic.ttf',
    'comic':'Comic Sans MS.ttf',
    'futura':'Futura.ttc',
    'helvetica':'HelveticaNeue.ttc',
    'times':'Times New Roman Italic.ttf'
}

positions = {

    0:'topright',
    1:'topleft',
    2:'bottomright',
    3:'bottomleft',
    4:'center'

}

def clearfolder():
    for f in os.listdir(UPLOAD_FOLDER):
        os.remove(os.path.join(UPLOAD_FOLDER, f))
    watermarks.clear()
    fontz.clear()
    fontz.append('Comic Sans MS.ttf')
    position.clear()
    position.append(2)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

clearfolder()

class Upload(Resource):
    def post(self):
        clearfolder()
        f = fontz[0]
        p = position[0]
        if 'watermark' not in request.form:
            resp = jsonify({'message': 'No watermark part in the request'})
            resp.status_code = 400
            return resp
        watermark = request.form.get("watermark")
        watermarks.append(watermark)

        if 'font' in request.form:
            f=request.form.get("font")
            f=f.lower()
            if f not in fonts:
                return jsonify({'message': "Error only fonts available below"},
                               fonts)
            else:
                fontz[0]=(fonts[f])
        if 'position' in request.form:
            p = request.form.get("position")
            p = int(p)
            if p not in positions:
                return jsonify({'message': "Error only positions available below"},
                               positions)
            else:
                position[0] = p
        print(position[0])

        if 'files[]' not in request.files:
            resp = jsonify({'message': 'No file part in the request'})
            resp.status_code = 400
            return resp
        files = request.files.getlist('files[]')

        errors = {}
        success = False

        for file in files:
            if file and allowed_file(file.filename):
                #filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], 'unwatermarked.jpg'))
                success = True
            else:
                errors[file.filename] = 'File type is not allowed'

        if success and errors:
            errors['message'] = 'File(s) successfully uploaded'
            resp = jsonify(errors)
            resp.status_code = 500
            return resp
        if success:
            resp = jsonify({'message': 'Files successfully uploaded'},
                           {
                            'watermark': watermark,
                            'font': f,
                            'position':positions[p]
                           })
            resp.status_code = 201
            return resp
        else:
            resp = jsonify(errors)
            resp.status_code = 500
            return resp

class Download(Resource):
    def get(self):

        img = Image.open('/images/unwatermarked.jpg')
        width, height = img.size

        draw = ImageDraw.Draw(img)
        text = watermarks[0]

        font = ImageFont.truetype(fontz[0], int(height / 20))

        textwidth, textheight = draw.textsize(text, font)

        difference = min(width / 30, height / 30)


        x = width - textwidth - difference
        y = height - textheight - difference

        if position[0] == 0:
            x = 0 + difference
            y = 0 + difference
        if position[0] == 1:
            x = width - textwidth - difference
            y = 0 + difference
        if position[0] == 3:
            x = 0 + difference
            y = height - textheight - difference
        if position[0]==4:
            x = width//2-textwidth/2
            y = height//2-textheight/2

        draw.text((x, y), text, font=font)

        # Saving the image
        img.save('/images/watermarked.jpg')

        return send_file(download_path,as_attachment=True)






api.add_resource(Upload,'/upload')
api.add_resource(Download,'/download')




app.run()





