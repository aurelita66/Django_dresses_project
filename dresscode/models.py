from django.db import models
from django.contrib.auth.models import User
from datetime import date
from PIL import Image
from tinymce.models import HTMLField


class Designer(models.Model):
    """ Dizainerio modelis

        Laukeliai:
            name (CharField): Dizainerio vardas.
            surname (CharField): Dizainerio pavardė.
            description (HTMLField): Dizainerio aprašymas (naudojant TinyMCE).
            designers_pics (ImageField): Dizainerio nuotrauka.
        Meta:
            ordering: Nurodo, kad dizaineriai bus rikiuojami pagal vardą ir pavardę."""

    name = models.CharField('Name', max_length=50)
    surname = models.CharField('Surname', max_length=50)
    description = HTMLField('Description', blank=True, null=True)
    designers_pics = models.ImageField('Photo', upload_to='designers_pics', null=True, blank=True)

    def __str__(self):
        return f"{self.name} {self.surname}"

    class Meta:
        ordering = ('name', 'surname')


class Size(models.Model):
    """ Dydžio modelis

        Laukeliai:
            name (CharField): Dydžio pavadinimas."""

    name = models.CharField('Name', max_length=50)

    def __str__(self):
        return f"{self.name}"


class Style(models.Model):
    """ Stiliaus modelis

       Laukeliai:
           name (CharField): Stiliaus pavadinimas."""

    name = models.CharField('Name', max_length=50)

    def __str__(self):
        return f"{self.name}"


class Dress(models.Model):
    """ Suknelės modelis

        Laukeliai:
              color (CharField): Suknelės spalva.
              item_code (CharField): Suknelės prekės kodas (unikalus).
              description (HTMLField): Suknelės aprašymas (naudojant TinyMCE).
              designer (ForeignKey): Dizainerio ryšys.
              sizes (ManyToManyField): Dydžių ryšys.
              styles (ManyToManyField): Stilių ryšys.
              dresses_pics (ImageField): Suknelės nuotrauka.

        Metodai:
              display_sizes(): Grąžina suknelės dydžių sąrašą kaip eilutę.
              display_styles(): Grąžina suknelės stilių sąrašą kaip eilutę.

        Meta:
              verbose_name: Vienaskaitos pavadinimas.
              verbose_name_plural: Daugiskaitos pavadinimas."""

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
    """ Suknelės nuomos modelis

       Laukeliai:
           start_date (DateField): Nuomos pradžios data.
           return_date (DateField): Grąžinimo data.
           dress (ForeignKey): Suknelės ryšys.
           user (ForeignKey): Vartotojo ryšys.
           size (ForeignKey): Dydžio ryšys.
           status (CharField): Nuomos statusas.

       Metodai:
           is_overdue (property): Tikrina ar suknelės grąžinimo data yra praėjusi."""

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
    """ Suknelės atsiliepimo modelis

        Laukeliai:
            date_created (DateTimeField): Atsiliepimo sukūrimo data.
            content (TextField): Atsiliepimo turinys.
            dress (ForeignKey): Suknelės ryšys.
            reviewer (ForeignKey): Atsiliepimo autoriaus ryšys."""

    date_created = models.DateTimeField(auto_now_add=True)
    content = models.TextField('Comment', max_length=2000)
    dress = models.ForeignKey(Dress, on_delete=models.CASCADE, blank=True)
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.date_created}, {self.reviewer}, {self.dress}, {self.content}"


class Profile(models.Model):
    """ Vartotojo profilio modelis

        Laukeliai:
            picture (ImageField): Profilio nuotrauka.
            user (OneToOneField): Vartotojo ryšys.
            iban (CharField): IBAN banko sąskaitos numeris.

        Metodai:
            save(): Automatiškai sumažina įkeliamas profilio nuotraukas."""

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
