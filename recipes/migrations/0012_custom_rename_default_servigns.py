from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0011_auto_20200410_1456')
    ]

    operations = [
        migrations.RenameField(
            model_name='recipe',
            old_name='default_servings',
            new_name='serves',
        )
    ]
