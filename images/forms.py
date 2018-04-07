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
