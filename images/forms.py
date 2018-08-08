from django import forms


class ImageForm(forms.ModelForm):

    class Meta:
        fields = [
            'title',
            'file',
            'focal_point_x',
            'focal_point_y',
            'focal_point_width',
            'focal_point_height'
        ]
        widgets = {
            'focal_point_x': forms.HiddenInput,
            'focal_point_y': forms.HiddenInput,
            'focal_point_width': forms.HiddenInput,
            'focal_point_height': forms.HiddenInput
        }

    class Media:
        css = {
            'all': (
                'images/css/Jcrop.min.css',
                'images/css/focal-point-chooser.css'
            )
        }
        js = (
            '//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js',
            'images/js/jquery.ba-throttle-debounce.min.js',
            'images/js/Jcrop.min.js',
            'images/js/auto-title.js',
            'images/js/focal-point-chooser.js',
        )
