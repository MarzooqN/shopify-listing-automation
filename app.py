from flask import Flask, render_template, request, redirect, url_for
from flask_uploads import UploadSet, configure_uploads, IMAGES
import csv
from io import TextIOWrapper
from shopify import ShopifyResource, Product, Session, Image, Variant, Option
from flask_socketio import SocketIO
import time

app = Flask(__name__)
socketio = SocketIO(app)

# Configuration for Flask-Uploads
photos = UploadSet('photos', IMAGES)
app.config['UPLOADED_PHOTOS_DEST'] = 'static/img'
configure_uploads(app, photos)

# In-memory database for demonstration purposes
products = []

def create_listings_with_photos(titles, price, description, photo_filenames):
    # Create listings with batches of 4 photos
    for i in range(0, len(photo_filenames), 4):
        # Extract 4 photos for the current batch
        batch_photos = photo_filenames[i:i+4]

        #Extract title from titles 
        title_index = i // 4
        title = titles[title_index % len(titles)]

        # Create a new product with the same title, price, and description
        new_product = {'name': title, 'price': price, 'description': description, 'images': batch_photos}
        
        # Add the new product to the database
        products.append(new_product)

@app.route('/')
def index():
    return render_template('index.html', products=products)



def create_shopify_listing(titles, prices, description, images, num_photos, colors, sizes):

    total_files = len(images)
    current_time = time.time()

    for i in range(0, len(images), num_photos):

        product = Product()

        #Extract title from titles 
        title_index = i // num_photos
        title = titles[title_index % len(titles)]

        price_index = i // num_photos
        price = prices[price_index % len(prices)]
        

        #Sets title and description 
        product.title = title
        product.body_html = description
        
        #Create options
        options = [] 
        color_options = Option()
        color_options.name = "Color"
        options.append(color_options)

        size_options = Option()
        size_options.name = "Sizes"
        options.append(size_options)

        product.options = options

        #Create Variants based on options
        variant_list = []
        for color in colors:
            for size in sizes:
                variant = Variant()
                variant.price = float(price)
                variant.option1 = color 
                variant.option2 = size 
                variant.compare_at_price = float(price) + 9.99
                variant_list.append(variant)

        product.variants = variant_list
        
        # Extract num_photos photos for the current batch
        batch_photos = images[i:i+num_photos]

        image_list = []
        for j in range(0, len(batch_photos)):

            image = Image()
            with open(f'/Users/marzooqnadeem/AutomationProject/static/{batch_photos[j]}', "rb") as f:
                filename = batch_photos[j].split("/")[-1:][0]
                encoded = f.read()
                image.attach_image(encoded, filename=filename)
                image_list.append(image)


        #Creates tag to show product was created through automation 
        product.tags = 'Cute Christmas Toad', 'Christmas Clothes', 'Gift for family', 'Gift for Friends', 'Mario Clothing', 'Christmas Gift', 'Santa Hat Toad', 'Cute Toad', 'Mario Peach', 'Christmas Luigi', 'Christmas Peach', 'Black Friday Mario', 'Santa Mario' 

        try:
            product.save()

            # Attach the images to the product using the product ID
            for img in image_list:
                img.product_id = product.id
                img.save()
            
            progress = int((i / total_files) * 100)

            socketio.emit('update_progress', {'progress': progress})
   
        except Exception as e:
            print(f"Error creating product: {e}")


    elapsed_time = time.time() - current_time
    print(elapsed_time)

def read_titles_from_csv(title_file):
    titles = []
    try:
        # Assuming the CSV file has one title per line
        # Use TextIOWrapper to treat the FileStorage object as a text file
        with TextIOWrapper(title_file, encoding='utf-8', newline='')  as file:
            reader = csv.reader(file)
            titles = [row[0] for row in reader]
    except Exception as e:
        print(f"Error reading titles from CSV file: {e}")
    return titles


@app.route('/create-listing', methods=['GET', 'POST'])
def create_listing():
    if request.method == 'POST':
        title = request.form.get('title')
        price = [price.strip() for price in request.form.get('price').split(',')]
        num_photos = int(request.form.get('num_photos'))
        colors =  [color.strip() for color in request.form.get('colors').split(',')]
        sizes =  [size.strip() for size in request.form.get('sizes').split(',')]
        description = request.form.get('description')

        # Handle file uploads (multiple photos and a CSV file for titles)
        uploaded_photos = request.files.getlist('photos')
        photo_filenames = []

        # Handle title uploads
        title_file = request.files.get('title_file')
        titles = read_titles_from_csv(title_file)

        for photo in uploaded_photos:
            if photo:
                filename = photos.save(photo)
                photo_filenames.append(f'img/{filename}')


        #Set up Shopify API
        shop_url = 'humraha.myshopify.com'
        admin_api_key = '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'
        api_version = '2024-01'

        #Create new session 
        session = Session(shop_url, api_version, admin_api_key)
        ShopifyResource.activate_session(session)

        # Create Shopify listing
        create_shopify_listing(titles, price, description, photo_filenames, num_photos, colors, sizes)

        ShopifyResource.clear_session()

        # Notify the client that processing is complete
        socketio.emit('update_progress', {'progress': 100})

    return render_template('create_listing.html')

if __name__ == '__main__':
    app.run(debug=True)
