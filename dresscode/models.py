from django.db import models
from django.contrib.auth.models import User
from datetime import date
from PIL import Image
from tinymce.models import HTMLField


class Designer(models.Model):
    name = models.CharField('Name', max_length=50)
    surname = models.CharField('Surname', max_length=50)
    description = HTMLField('Description', blank=True, null=True)
    designers_pics = models.ImageField('Photo', upload_to='designers_pics', null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.surname}"

    class Meta:
        ordering = ('name', 'surname')


class Size(models.Model):
    name = models.CharField('Name', max_length=50)

    def __str__(self):
        return f"{self.name}"


class Style(models.Model):
    name = models.CharField('Name', max_length=50)

    def __str__(self):
        return f"{self.name}"


class Dress(models.Model):
    color = models.CharField('Color', max_length=50)
    item_code = models.CharField('Item code', max_length=10, unique=True)
    description = HTMLField('Description', blank=True, null=True)
    designer = models.ForeignKey(Designer, on_delete=models.CASCADE)
    sizes = models.ManyToManyField(Size)
    styles = models.ManyToManyField(Style)
    dresses_pics = models.ImageField('Photo', upload_to='dresses_pics', null=True, blank=True)

    def display_sizes(self):
        """Grąžina suknelės dydžių sąrašą"""
        res = ', '.join(elem.name for elem in self.sizes.all())
        return res

    def display_styles(self):
        """Grąžina suknelės stilių sąrašą"""
        res = ', '.join(elem.name for elem in self.styles.all())
        return res

    def __str__(self):
        return f"{self.item_code}"

    class Meta:
        verbose_name = "Dress"
        verbose_name_plural = "Dresses"


class DressRental(models.Model):
    start_date = models.DateField('Start day', null=True, blank=True)
    return_date = models.DateField('Return day', null=True, blank=True)
    dress = models.ForeignKey(Dress, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True)

    RENTAL_STATUS = (
        ('pending', 'pending'),
        ('approved', 'approved'),
        ('rented', 'rented'),
        ('returned', 'returned')
    )

    status = models.CharField('Status',
                              max_length=20,
                              choices=RENTAL_STATUS,
                              default='pending',
                              blank=True,
                              help_text='Dress rent status')

    @property
    def is_overdue(self):
        """Tikrina ar suknelės grąžinimo data yra praėjusi"""
        if self.return_date and date.today() > self.return_date:
            return True
        else:
            return False

    def __str__(self):
        return f"{self.dress} {self.size} {self.user} {self.status} {self.return_date}"


class DressReview(models.Model):
    date_created = models.DateTimeField(auto_now_add=True)
    content = models.TextField('Comment', max_length=2000)
    dress = models.ForeignKey(Dress, on_delete=models.CASCADE, blank=True)
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.date_created}, {self.reviewer}, {self.dress}, {self.content}"


class Profile(models.Model):
    picture = models.ImageField(upload_to='profile_pics', default='default-user.png')
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    iban = models.CharField('IBAN', max_length=50)

    def __str__(self):
        return f"{self.user.username} profile"

    def save(self, *args, **kwargs):
        """Automatiškai sumažina įkeliamas profilio nuotraukas,
        kad taupytų vietą serveryje"""
        super().save(*args, **kwargs)
        if self.picture.path:
            img = Image.open(self.picture.path)
            thumb_size = (150, 150)
            img.thumbnail(thumb_size)
            img.save(self.picture.path)
