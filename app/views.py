import csv
import json
import mimetypes
import pickle
import re

from django.http import HttpResponse
from . import models
from urllib.request import urlopen
from bs4 import BeautifulSoup


def get_page(page_url):
    html = urlopen(page_url)
    bs = BeautifulSoup(html, 'html.parser')
    return bs


def create_csv(filename, fieldnames, objects_list):
    with open(filename, 'w', encoding='UTF8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(fieldnames)
        writer.writerows(objects_list)


def download_files(filename):
    path = open(filename, 'r')
    mime_type, _ = mimetypes.guess_type(filename)
    response = HttpResponse(path, content_type=mime_type)
    response['Content-Disposition'] = "attachment; filename=%s" % filename
    return response


def get_objects():
    main_url = 'https://api.torob.com/v4/base-product/search/?sort=popularity&category=94&page=&size=24&source=next&_bt__experiment='

    mor_info_url_list = []
    names_list = []

    for i in range(0, 5):
        page_url = main_url[:79] + str(i) + main_url[79:]
        bs = get_page(page_url)

        data = json.loads(str(bs))

        for j in range(0, 24):
            url = data['results'][j]['random_key'] + '/' + data['results'][j]['name1'].replace(' |', '')

            if data['results'][j]['name1'] not in names_list:
                try:
                    count_of_merchant = int(re.search(r'\d+', data['results'][j]['shop_text']).group())
                except AttributeError:
                    count_of_merchant = 1

                obj = models.Source_Product(name=data['results'][j]['name1'].replace(' |', ''), price=data['results'][j]['price'], url_address=url, count_of_merchant=count_of_merchant)
                obj.save()

                mor_info_url_list.append(data['results'][j]['more_info_url'])
                names_list.append(data['results'][j]['name1'])

    with open("more_info_url.txt", "wb") as fp:
        pickle.dump(mor_info_url_list, fp)


def get_merchants():
    with open("more_info_url.txt", "rb") as fp:
        mor_info_urls = pickle.load(fp)

    for product_url in mor_info_urls:
        bs = get_page(product_url)

        data = json.loads(str(bs))

        for item in data['products_info']['result']:
            try:
                obj = models.Merchant.objects.get(name=item['shop_name'])
            except models.Merchant.DoesNotExist:
                obj = models.Merchant(name=item['shop_name'], city=item['shop_name2'], score=item['shop_score'])
                obj.save()


def get_price_list():
    with open("more_info_url.txt", "rb") as fp:
        mor_info_urls = pickle.load(fp)

    for product_url in mor_info_urls:
        bs = get_page(product_url)

        data = json.loads(str(bs))

        product_id = models.Source_Product.objects.get(name=data['name1'].replace(' |', '')).id

        for item in data['products_info']['result']:
            try:
                merchant_id = models.Merchant.objects.get(name=item['shop_name']).id
            except models.Merchant.DoesNotExist:
                pass
            else:
                flag = True
                if not item['price_string']:
                    flag = False

                price_obj = models.Price_list(source_product_id=product_id, merchant_id=merchant_id, product_description=item['name1'], remark=item['name2'], price=item['price'], in_stock_status=flag)
                price_obj.save()


def mobiles_list(request):
    models.Source_Product.objects.all().delete()

    get_objects()
    return HttpResponse('All mobiles are saved :)')


def mobiles_list_download(request):
    objects = models.Source_Product.objects.all()

    objects_list = []

    for obj in objects:
        fields_list = [obj.id, obj.name, obj.price, obj.count_of_merchant, 'http://torob.com/p/' + obj.url_address]
        objects_list.append(fields_list)

    fieldnames = ['id', 'name', 'price', 'count_of_merchant', 'url_address']

    create_csv('source_products.csv', fieldnames, objects_list)

    response = download_files('source_products.csv')
    return response


def merchants_list(request):
    models.Merchant.objects.all().delete()

    get_merchants()

    return HttpResponse('All merchants are saved :)')


def price_list(request):
    models.Price_list.objects.all().delete()

    get_price_list()

    return HttpResponse('All price_lists are saved :)')


def merchants_list_download(request):
    merchants = models.Merchant.objects.all()

    objects_list = []

    for merchant in merchants:
        number_of_products = models.Price_list.objects.all().filter(merchant_id=merchant.id).count()

        fields_list = [merchant.id, merchant.name, merchant.city, merchant.score, number_of_products]
        objects_list.append(fields_list)

    fieldnames = ['id', 'name', 'city', 'score', 'number_of_products']

    create_csv('merchants.csv', fieldnames, objects_list)

    response = download_files('merchants.csv')
    return response
