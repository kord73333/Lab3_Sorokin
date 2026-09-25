from django import forms
from .models import Movie


class MovieForm(forms.ModelForm):
    FORMAT_CHOICES = [
        ('json', 'JSON'),
        ('xml', 'XML'),
    ]
    file_format = forms.ChoiceField(
        choices=FORMAT_CHOICES, label='Формат файла', initial='json'
    )

    class Meta:
        model = Movie
        fields = ['title', 'director', 'year', 'genre', 'rating']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'director': forms.TextInput(attrs={'class': 'form-control'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'genre': forms.TextInput(attrs={'class': 'form-control'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}),
        }

    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if len(title) < 1:
            raise forms.ValidationError('Название не может быть пустым')
        if len(title) > 200:
            raise forms.ValidationError('Слишком длинное название')
        return title

    def clean_director(self):
        director = self.cleaned_data['director'].strip()
        if len(director) < 2:
            raise forms.ValidationError('Имя режиссёра слишком короткое')
        return director

    def clean_year(self):
        year = self.cleaned_data['year']
        if year < 1888 or year > 2100:
            raise forms.ValidationError('Год должен быть между 1888 и 2100')
        return year

    def clean_rating(self):
        rating = self.cleaned_data['rating']
        if not (0 <= rating <= 10):
            raise forms.ValidationError('Рейтинг должен быть от 0 до 10')
        return rating