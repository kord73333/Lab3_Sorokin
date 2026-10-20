from django import forms

from .models import Movie

FORMAT_CHOICES = [
    ('json', 'JSON'),
    ('xml', 'XML'),
]

TARGET_CHOICES = [
    ('file', 'Файл (JSON/XML)'),
    ('db', 'База данных SQLite'),
]

TEXT_WIDGET = forms.TextInput(attrs={'class': 'form-control'})


class MovieValidationMixin:

    def clean_title(self):
        title = self.cleaned_data['title'].strip()
        if not title:
            raise forms.ValidationError('Название не может быть пустым')
        if len(title) > 200:
            raise forms.ValidationError(
                'Слишком длинное название (максимум 200 символов)'
            )
        return title

    def clean_director(self):
        director = self.cleaned_data['director'].strip()
        if len(director) < 2:
            raise forms.ValidationError(
                'Имя режиссёра слишком короткое (минимум 2 символа)'
            )
        if len(director) > 200:
            raise forms.ValidationError(
                'Слишком длинное имя режиссёра (максимум 200 символов)'
            )
        return director

    def clean_genre(self):
        genre = self.cleaned_data['genre'].strip()
        if not genre:
            raise forms.ValidationError('Жанр не может быть пустым')
        if len(genre) > 100:
            raise forms.ValidationError(
                'Слишком длинное название жанра (максимум 100 символов)'
            )
        return genre

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


class MovieForm(MovieValidationMixin, forms.ModelForm):

    save_target = forms.ChoiceField(
        choices=TARGET_CHOICES,
        label='Куда сохранить',
        initial='db',
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'}),
    )
    file_format = forms.ChoiceField(
        choices=FORMAT_CHOICES,
        label='Формат файла',
        initial='json',
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
    )

    class Meta:
        model = Movie
        fields = ['title', 'director', 'year', 'genre', 'rating']
        widgets = {
            'title': TEXT_WIDGET,
            'director': TEXT_WIDGET,
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'genre': TEXT_WIDGET,
            'rating': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.1'}
            ),
        }

    def clean(self):
        cleaned = super().clean()
        target = cleaned.get('save_target')
        fmt = cleaned.get('file_format')
        if target == 'file' and not fmt:
            self.add_error('file_format', 'Выберите формат файла')
        return cleaned


class MovieEditForm(MovieValidationMixin, forms.ModelForm):
    class Meta:
        model = Movie
        fields = ['title', 'director', 'year', 'genre', 'rating']
        widgets = {
            'title': TEXT_WIDGET,
            'director': TEXT_WIDGET,
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'genre': TEXT_WIDGET,
            'rating': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '0.1'}
            ),
        }
