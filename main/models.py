from django.db import models
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name
    


class Product(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='products')
    price = models.DecimalField(max_digits=100, decimal_places=2)
    description = models.TextField(blank=True)
    main_image = models.ImageField(upload_to='products')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


    def __str__(self):
        return self.name
    


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                 related_name='images')
    image = models.ImageField(upload_to='products/extra/')

