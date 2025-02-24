from django import forms

from .models import DressReview, Profile, User, DressRental, Size


class DressReviewForm(forms.ModelForm):
    """Sukuria formą atsiliepimams apie sukneles,
    slepiant suknelės ir atsiliepimo autoriaus laukus."""
    class Meta:
        model = DressReview
        fields = ('content', 'dress', 'reviewer')
        widgets = {
            'dress': forms.HiddenInput(),
            'reviewer': forms.HiddenInput()
        }


class ProfileUpdateForm(forms.ModelForm):
    """Sukuria formą vartotojo profilio nuotraukos ir IBAN atnaujinimui."""
    class Meta:
        model = Profile
        fields = ('picture', 'iban')


class UserUpdateForm(forms.ModelForm):
    """Sukuria formą vartotojo el.pašto, vardo ir pavardės atnaujinimui."""
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')


class DateInput(forms.DateInput):
    input_type = 'date'


class UserDressRentalCreateForm(forms.ModelForm):
    """Sukuria formą suknelės nuomai, slepiant vartotojo ir statuso laukus,
    tačiau leidžiant pasirinkti suknelę, pradžios ir pabaigos datas, dydį."""
    size = forms.ModelChoiceField(queryset=Size.objects.none(), empty_label="--------")

    class Meta:
        model = DressRental
        fields = ('dress', 'user', 'start_date', 'return_date', 'status', 'size')
        widgets = {
            'user': forms.HiddenInput(),
            'status': forms.HiddenInput(),
            'start_date': DateInput(),
            'return_date': DateInput()
        }

    def __init__(self, *args, **kwargs):
        """inicijuoja suknelės nuomos formą, neleidžia keisti suknelės ir pradžios datos, dydžio,
        jei tai yra esamos suknelės nuomos atnaujinimas. Neleidžia keisti suknelės,
        jei tai yra naujos suknelės nuomos forma per tos suknelės puslapį."""

        dress = kwargs.pop('dress', None)  # perduodam pasirinktą suknelę į formą
        super().__init__(*args, **kwargs)

        if self.instance.pk:  # Jei atnaujiname esamą suknelės nuomos formą
            self.fields['dress'].disabled = True
            self.fields['start_date'].disabled = True
            self.fields['size'].disabled = True

            if self.instance.size:  # Jei buvo pasirinktas dydis, nustatome jį
                self.fields['size'].queryset = Size.objects.filter(id=self.instance.size.id)
                self.fields['size'].initial = self.instance.size  # pradinė reikšmė pagal jau pasirinkto dydžio objektą

        elif dress:  # Jei kuriame naują nuomos formą per suknelės puslapį
            self.fields['dress'].initial = dress
            self.fields['dress'].disabled = True
            self.fields['size'].queryset = dress.sizes.all()  # tik pasirinktos suknelės dydžiai
