from PIL import Image
from django import forms
from django.core.files import File
from .models import Profile


class PhotoForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())
    user = forms.CharField(widget=forms.HiddenInput())

    class Meta:
        model = Profile
        fields = ('file', 'x', 'y', 'width', 'height', 'user')

    def save(self):
        photo = super(PhotoForm, self).save()

        x = self.cleaned_data.get('x')
        y = self.cleaned_data.get('y')
        w = self.cleaned_data.get('width')
        h = self.cleaned_data.get('height')

        image = Image.open(photo.file)
        cropped_image = image.crop((x, y, w + x, h + y))
        resized_image = cropped_image.resize((200, 200), Image.ANTIALIAS)
        print(photo.file.path)
        resized_image.save(photo.file.path)

        return photo
