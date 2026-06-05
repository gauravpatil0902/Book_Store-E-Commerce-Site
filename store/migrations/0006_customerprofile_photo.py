from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("store", "0005_customerprofile_photo_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="customerprofile",
            name="photo",
            field=models.FileField(blank=True, upload_to="profile_photos/"),
        ),
    ]
