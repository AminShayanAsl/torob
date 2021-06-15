from django.db import models


class Source_Product(models.Model):
    name = models.CharField(max_length=256, null=False)
    price = models.IntegerField(null=False)
    url_address = models.CharField(max_length=512, null=True)
    count_of_merchant = models.IntegerField(null=False)


class Merchant(models.Model):
    name = models.CharField(max_length=256, null=False)
    city = models.CharField(max_length=256, null=False, default='unknown')
    score = models.IntegerField(null=False)


class Price_list(models.Model):
    source_product_id = models.IntegerField(null=False)
    merchant_id = models.IntegerField(null=False)
    product_description = models.CharField(max_length=512, null=False)
    remark = models.CharField(max_length=512, null=False, default='empty')
    price = models.IntegerField(null=False)
    in_stock_status = models.BooleanField(default=True)
