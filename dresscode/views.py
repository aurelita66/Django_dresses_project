from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.views import generic
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required

from .models import Designer, Dress, DressRental, User, DressReview, Profile
from .forms import DressReviewForm, ProfileUpdateForm, UserUpdateForm, UserDressRentalCreateForm
from .utils import check_password


def index(request):
    """
       Rodo pagrindinį puslapį su statistika, jei vartotojas prisijungęs,
       o jei neprisijungęs nukreipia į registracijos puslapį.

       Funkcijos logika:
           1. Tikrinama, ar vartotojas yra prisijungęs (request.user.is_authenticated).
           2. Jei vartotojas yra prisijungęs:
               Skaičiuojamas dizainerių, suknelių, nuomos įrašų, išnuomotų ir grąžintų suknelių skaičius.
               Sukuriamas kontekstas su šiais duomenimis.
               Atvaizduojamas 'index.html' šablonas su kontekstu.
           3. Jei vartotojas nėra prisijungęs:
               Nukreipiama į registracijos puslapį (redirect('register')).
    """
    if request.user.is_authenticated:
        num_designers = Designer.objects.count()
        num_dresses = Dress.objects.count()
        num_dress_rentals = DressRental.objects.count()
        num_dresses_rented = DressRental.objects.filter(status__exact='rented').count()
        num_dresses_returned = DressRental.objects.filter(status__exact='returned').count()

        context = {'num_designers': num_designers,
                   'num_dresses': num_dresses,
                   'num_dress_rentals': num_dress_rentals,
                   'num_dresses_rented': num_dresses_rented,
                   'num_dresses_returned': num_dresses_returned
                   }

        return render(request, 'index.html', context=context)

    else:
        return redirect('register')


def get_designers(request):
    """
        Gauna visus dizainerius, suskirsto juos į puslapius ir rodo dizainerių sąrašą.

        Funkcijos logika:
            1. Gaunami visi dizaineriai iš duomenų bazės (Designer.objects.all()).
            2. Sukuriamas puslapiavimo objektas (Paginator), kuris suskirsto dizainerius į puslapius.
            3. Gaunamas puslapio numeris iš užklausos (request.GET.get('page')).
            4. Gaunamas puslapis su dizaineriais pagal puslapio numerį (paginator.get_page(page_number)).
            5. Sukuriamas kontekstas su puslapiuotu dizainerių sąrašu.
            6. Atvaizduojamas 'designers.html' šablonas su kontekstu.
    """
    designers = Designer.objects.all()
    paginator = Paginator(designers, 2)
    page_number = request.GET.get('page')
    paged_designers = paginator.get_page(page_number)
    context = {'designers': paged_designers}
    return render(request, 'designers.html', context=context)


def get_one_designer(request, designer_id):
    """
        Gauna vieną dizainerį pagal ID ir rodo jo informaciją.

        Funkcijos logika:
            1. Gaunamas dizaineris iš duomenų bazės pagal ID (get_object_or_404(Designer, pk=designer_id)).
            2. Sukuriamas kontekstas su dizainerio informacija.
            3. Atvaizduojamas 'designer.html' šablonas su kontekstu.
    """
    one_designer = get_object_or_404(Designer, pk=designer_id)
    context = {'one_designer': one_designer}
    return render(request, 'designer.html', context=context)


class DressListView(generic.ListView):
    """
       Rodo suknelių sąrašą, suskirstytą į puslapius.

       Klasės kintamieji:
           model (Model): Modelis, iš kurio gaunami objektai (Dress).
           context_object_name (str): Konteksto kintamojo pavadinimas ('dress_list').
           template_name (str): Šablono pavadinimas ('dresses.html').
           paginate_by (int): Objektų skaičius viename puslapyje (4).

       Metodai:
           get_queryset(): Gauna suknelių sąrašą iš duomenų bazės.
    """
    model = Dress
    context_object_name = 'dress_list'
    template_name = 'dresses.html'
    paginate_by = 4


class DressDetailView(generic.edit.FormMixin, generic.DetailView):
    """
       Rodo suknelės detalę informaciją ir leidžia vartotojams palikti atsiliepimą.

       Klasės kintamieji:
           model (Model): Modelis, iš kurio gaunamas objektas (Dress).
           context_object_name (str): Konteksto kintamojo pavadinimas ('dress').
           template_name (str): Šablono pavadinimas ('dress.html').
           form_class (Form): Atsiliepimo forma (DressReviewForm).

       Metodai:
           post(): Apdoroja atsiliepimo formos pateikimą.
           form_valid(): Išsaugo atsiliepimą, susieja jį su suknele ir vartotoju.
           get_success_url(): Nukreipia į suknelės puslapį po sėkmingo atsiliepimo palikimo.
    """
    model = Dress
    context_object_name = 'dress'
    template_name = 'dress.html'
    form_class = DressReviewForm

    def post(self, request, *args, **kwargs):
        """Apdoroja atsiliepimo formos pateikimą."""
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """Išsaugo atsiliepimą, susieja jį su suknele ir vartotoju."""
        self.dress_object = self.get_object()
        form.instance.dress = self.dress_object
        form.instance.reviewer = self.request.user
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Nukreipia į suknelės puslapį po sėkmingo atsiliepimo palikimo."""
        return reverse('dress-one', kwargs={'pk': self.dress_object.id})


def search(request):
    """
        Ieško suknelių pagal spalvą, stilių, prekės kodą ir rodo rezultatus.

        Funkcijos logika:
            1. Gaunamas paieškos tekstas iš užklausos (request.GET.get('search_text')).
            2. Ieškoma suknelių, kurių spalva, stilius arba prekės kodas atitinka paieškos tekstą.
            3. Sukuriamas kontekstas su paieškos tekstu ir rezultatais.
            4. Atvaizduojamas 'search_results.html' šablonas su kontekstu.
    """
    query_text = request.GET.get('search_text')
    search_results = Dress.objects.filter(
        Q(color__icontains=query_text)
        | Q(styles__name__icontains=query_text)
        | Q(item_code__icontains=query_text)
    ).distinct()

    context = {'query_text': query_text,
               'dress_list': search_results}

    return render(request, 'search_results.html', context=context)


class RentedDressesByUserListView(LoginRequiredMixin, generic.ListView):
    """
        Rodo prisijungusio vartotojo išsinuomotas sukneles.

        Klasės kintamieji:
            model (Model): Modelis, iš kurio gaunami objektai (DressRental).
            context_object_name (str): Konteksto kintamojo pavadinimas ('dressrental_list').
            template_name (str): Šablono pavadinimas ('user_dresses.html').

        Metodai:
            get_queryset(): Gauna prisijungusio vartotojo išsinuomotas sukneles.
    """
    model = DressRental
    context_object_name = 'dressrental_list'
    template_name = 'user_dresses.html'

    def get_queryset(self):
        """Gauna prisijungusio vartotojo išsinuomotas sukneles."""
        return DressRental.objects.filter(user=self.request.user)


@csrf_protect
def register_user(request):
    """
        Registruoja naują vartotoją, tikrina ar sutampa slaptažodžiai,
        ar neegzistuoja jau toks username, el.paštas, ar iban laukelis netuščias.

        Funkcijos logika:
            1. Jei užklausa yra GET, atvaizduojamas registracijos šablonas.
            2. Jei užklausa yra POST:
                Gaunami duomenys iš formos.
                Tikrinama, ar slaptažodžiai sutampa, ar neegzistuoja jau toks vartotojo vardas
                  arba el. paštas, ar IBAN laukelis nėra tuščias.
                Jei yra klaidų, rodomi pranešimai ir nukreipiama atgal į registracijos puslapį.
                Jei nėra klaidų, sukuriamas naujas vartotojas ir jo profilis.
                Rodomas pranešimas apie sėkmingą registraciją ir nukreipiama į prisijungimo puslapį.
    """
    if request.method == 'GET':
        return render(request, 'registration/registration.html')

    elif request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        iban = request.POST.get('iban')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if not check_password(password):
            messages.error(request, 'Password is minimum 8 symbols!!!')
            return redirect('register')

        if password != password2:
            messages.error(request, 'Passwords do not match, please retype passwords!')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username {username} already exists')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, f'Email {email} already exists')
            return redirect('register')

        if not iban:
            messages.error(request, 'You must enter IBAN number!')
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password, first_name=first_name,
                                        last_name=last_name)

        profile = Profile.objects.get(user=user)
        profile.iban = iban
        profile.save()

        messages.info(request, f'Username {username} is successfully registered!')
        return redirect('login')


@login_required
@csrf_protect
def get_user_profile(request):
    """
        Rodo ir leidžia redaguoti prisijungusiam vartotojui profilį.

        Funkcijos logika:
            1. Jei užklausa yra POST:
                * Gaunamos formos duomenys.
                * Tikrinama, ar formos yra validžios.
                * Jei formos yra validžios, išsaugomi duomenys ir rodomas pranešimas apie sėkmingą atnaujinimą.
                * Jei formos nėra validžios, rodomas pranešimas apie klaidą.
                * Nukreipiama į profilio puslapį.
            2. Jei užklausa yra GET:
                * Sukuriamos formos su esamais vartotojo duomenimis.
                * Atvaizduojamas profilio šablonas su formomis.
        """
    if request.method == 'POST':
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        u_form = UserUpdateForm(request.POST, instance=request.user)
        if p_form.is_valid() and u_form.is_valid():
            p_form.save()
            u_form.save()
            messages.info(request, "Profile updated!")
        else:
            messages.error(request, "Profile NOT updated")
        return redirect('user-profile')

    p_form = ProfileUpdateForm(instance=request.user.profile)
    u_form = UserUpdateForm(instance=request.user)

    context = {
        'p_form': p_form,
        'u_form': u_form
    }

    return render(request, 'profile.html', context=context)


class DressRentalByUserCreateView(LoginRequiredMixin, generic.CreateView):
    """
        Leidžia prisijungusiam vartotojui išsinuomoti suknelę,
        sukuriant naują įrašą DressRental modelyje.

        Klasės kintamieji:
            model (Model): Modelis, kuriame bus sukurtas naujas objektas (DressRental).
            form_class (Form): Suknelės nuomos forma (UserDressRentalCreateForm).
            template_name (str): Šablono pavadinimas ('user_dress_form_create.html').
            success_url (str): URL, į kurį nukreipiama po sėkmingo sukūrimo.

        Metodai:
            get_form_kwargs(): Gauna suknelės ID ir perduoda jį formai.
            form_valid(): Nustato prisijungusį vartotoją ir nuomos statusą.
    """
    model = DressRental
    form_class = UserDressRentalCreateForm
    template_name = 'user_dress_form_create.html'
    success_url = '/dresscode/mydresses'

    def get_form_kwargs(self):
        """Gauna suknelės ID ir perduoda jį formai,
        kad būtų iš anksto užpildyta suknelės informacija."""

        kwargs = super().get_form_kwargs()  # Iškviečia get_form_kwargs() iš tėvinės klasės CreateView
        dress_id = self.kwargs.get('pk') or self.request.GET.get('dress_id')  # Bandome gauti suknelės ID
        if dress_id:  # Tikrinam, ar gautas dress_id nėra None
            kwargs['dress'] = Dress.objects.prefetch_related('sizes').get(id=dress_id)  # Gaunam suknelės dress_id
        return kwargs  # Grąžina kwargs su papildomu 'dress' rakto įrašu

    def form_valid(self, form):
        """Nustato prisijungusį vartotoją, taip pat nustato
        ir išsaugo nuomos statusą 'pending' ."""
        form.instance.user = self.request.user
        form.instance.status = 'pending'
        return super().form_valid(form)


class DressRentalByUserUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    """
        Leidžia prisijungusiam vartotojui redaguoti savo suknelių nuomos įrašus.

        Klasės kintamieji:
            model (Model): Modelis, kuriame bus atnaujintas objektas (DressRental).
            form_class (Form): Suknelės nuomos forma (UserDressRentalCreateForm).
            template_name (str): Šablono pavadinimas ('user_dress_form_update.html').
            success_url (str): URL, į kurį nukreipiama po sėkmingo atnaujinimo.

        Metodai:
            form_valid(): Nustato prisijungusį vartotoją ir nuomos statusą.
            test_func(): Tikrina, ar vartotojas yra nuomos įrašo savininkas.
    """
    model = DressRental
    form_class = UserDressRentalCreateForm
    template_name = 'user_dress_form_update.html'
    success_url = '/dresscode/mydresses'

    def form_valid(self, form):
        """Nustato prisijungusį vartotoją ir nuomos statusą 'pending' atnaujinant suknelės įrašą."""
        form.instance.user = self.request.user
        form.instance.status = 'pending'
        return super().form_valid(form)

    def test_func(self):
        """Tikrina, ar prisijungęs vartotojas yra suknelės nuomos įrašo savininkas,
        kad leistų jam redaguoti."""
        dressrental_object = self.get_object()
        return dressrental_object.user == self.request.user


class DressReviewDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    """
        Leidžia admin ištrinti atsiliepimus apie sukneles.

        Klasės kintamieji:
            model (Model): Modelis, kuriame bus ištrintas objektas (DressReview).
            template_name (str): Šablono pavadinimas ('staff_dressreview_delete.html').
            context_object_name (str): Konteksto kintamojo pavadinimas ('dressreview').

        Metodai:
            get_success_url(): Nukreipia į suknelės puslapį po atsiliepimo ištrynimo.
            test_func(): Tikrina, ar vartotojas priklauso 'staff' grupei.
    """
    model = DressReview
    template_name = 'staff_dressreview_delete.html'
    context_object_name = 'dressreview'

    def get_success_url(self):
        """Nukreipia atgal į suknelės puslapį po atsiliepimo ištrynimo."""
        dressreview_object = self.get_object()
        return reverse('dress-one', kwargs={'pk': dressreview_object.dress.id})

    def test_func(self):
        """Tikrina, ar prisijungęs vartotojas priklauso 'staff' grupei,
        kad leistų jam ištrinti atsiliepimus."""
        check = False
        for group in self.request.user.groups.all():
            if group.name == 'staff':
                check = True
        return check


class AllRentsView(LoginRequiredMixin, UserPassesTestMixin, generic.TemplateView):
    """
        Rodo visų suknelių nuomos įrašų sąrašą, pasiekiama tik prisijungusiems vartotojams,
        kurie priklauso "moderators" grupei.

        Klasės kintamieji:
            template_name (str): Šablono pavadinimas ('all_rents.html').

        Metodai:
            get_context_data(): Prideda 'dress_rentals' kintamąjį į kontekstą.
            test_func(): Tikrina, ar vartotojas priklauso 'moderators' grupei.
    """
    template_name = 'all_rents.html'

    def get_context_data(self, **kwargs):
        """Prideda dress_rentals kintamąjį, kuriame yra visi DressRental objektai"""
        context = super().get_context_data(**kwargs)
        context['dress_rentals'] = DressRental.objects.all()
        return context

    def test_func(self):
        """Tikrina ar prisijungęs vartotojas priklauso 'moderators' grupei"""
        check = False
        for group in self.request.user.groups.all():
            if group.name == 'moderators':
                check = True
        return check


class DressRentalDeleteView(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    """
        Leidžia moderatoriams ištrinti nuomos įrašus.

        Klasės kintamieji:
            model (Model): Modelis, kuriame bus ištrintas objektas (DressRental).
            template_name (str): Šablono pavadinimas ('moderator_dressrental_delete.html').
            context_object_name (str): Konteksto kintamojo pavadinimas ('dressrental').

        Metodai:
            test_func(): Tikrina, ar vartotojas priklauso 'moderators' grupei.
            get_success_url(): Nukreipia atgal į nuomų įrašų puslapį po įrašo ištrynimo.
    """
    model = DressRental
    template_name = 'moderator_dressrental_delete.html'
    context_object_name = 'dressrental'

    def test_func(self):
        """Tikrina ar prisijungęs vartotojas priklauso 'moderators' grupei"""
        check = False
        for group in self.request.user.groups.all():
            if group.name == 'moderators':
                check = True
        return check

    def get_success_url(self):
        """Nukreipia atgal į nuomų įrašų puslapį po įrašo ištrynimo"""
        return reverse('allrents')


class DressRentalUpdateView(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    """
        Leidžia moderatoriams redaguoti nuomos įrašų statusus.

        Klasės kintamieji:
            model (Model): Modelis, kuriame bus atnaujintas objektas (DressRental).
            fields (list): Laukų, kuriuos galima redaguoti, sąrašas (['status']).
            template_name (str): Šablono pavadinimas ('moderator_dressrental_update.html').
            context_object_name (str): Konteksto kintamojo pavadinimas ('dressrental').

        Metodai:
            test_func(): Tikrina, ar vartotojas priklauso 'moderators' grupei.
            form_valid(): Nukreipia atgal į nuomų įrašų puslapį po įrašo atnaujinimo.
    """
    model = DressRental
    fields = ['status']
    template_name = 'moderator_dressrental_update.html'
    context_object_name = 'dressrental'

    def test_func(self):
        """Tikrina ar prisijungęs vartotojas priklauso 'moderators' grupei"""
        check = False
        for group in self.request.user.groups.all():
            if group.name == 'moderators':
                check = True
        return check

    def form_valid(self, form):
        """Nukreipia atgal į nuomų įrašų puslapį po įrašo atnaujinimo"""
        form.save()
        return redirect('allrents')
