import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='movie',
            options={
                'ordering': ['-created_at', '-id'],
                'verbose_name': 'Фильм',
                'verbose_name_plural': 'Фильмы',
            },
        ),
        migrations.AddField(
            model_name='movie',
            name='created_at',
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
                verbose_name='Дата добавления',
            ),
            preserve_default=False,
        ),
        migrations.AddConstraint(
            model_name='movie',
            constraint=models.UniqueConstraint(
                fields=('title', 'director', 'year'),
                name='unique_movie_title_director_year',
            ),
        ),
    ]
