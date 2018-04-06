from django import template

from images.models import Image
from tests.data import get_temporary_image
from tests.test_case import AppTestCase


class TestImageTag(AppTestCase):
    def setUp(self):
        # Create an image for running tests on
        self.image = Image.objects.create(
            title="Test image",
            file=get_temporary_image(),
        )

    def render_image_tag(self, image, filter_spec):
        temp = template.Template('{% load images_tags %}{% image image_obj ' + filter_spec + '%}')
        context = template.Context({'image_obj': image})
        return temp.render(context)

    def render_image_tag_as(self, image, filter_spec):
        temp = template.Template(
            '{% load images_tags %}{% image image_obj ' + filter_spec +
            ' as test_img %}<img {{ test_img.attrs }} />'
        )
        context = template.Context({'image_obj': image})
        return temp.render(context)

    def render_image_tag_with_extra_attributes(self, image, title):
        temp = template.Template(
            '{% load images_tags %}{% image image_obj width-400 \
            class="photo" title=title|lower alt="Alternate" %}'
        )
        context = template.Context({'image_obj': image, 'title': title})
        return temp.render(context)

    def render_image_tag_with_filters(self, image):
        temp = template.Template(
            '{% load images_tags %}{% image image_primary|default:image_alternate width-200 %}'
        )
        context = template.Context({'image_primary': None, 'image_alternate': image})
        return temp.render(context)

    def test_image_tag(self):
        result = self.render_image_tag(self.image, 'width-400')

        # Check that all the required HTML attributes are set
        self.assertTrue('width="400"' in result)
        self.assertTrue('height="200"' in result)
        self.assertTrue('alt="Test image"' in result)

    def test_image_tag_none(self):
        result = self.render_image_tag(None, "width-500")
        self.assertEqual(result, '')

    def test_image_tag_attrs(self):
        result = self.render_image_tag_as(self.image, 'width-400')

        # Check that all the required HTML attributes are set
        self.assertTrue('width="400"' in result)
        self.assertTrue('height="200"' in result)
        self.assertTrue('alt="Test image"' in result)

    def test_image_tag_with_extra_attributes(self):
        result = self.render_image_tag_with_extra_attributes(self.image, 'My Wonderful Title')

        # Check that all the required HTML attributes are set
        self.assertTrue('width="400"' in result)
        self.assertTrue('height="200"' in result)
        self.assertTrue('class="photo"' in result)
        self.assertTrue('alt="Alternate"' in result)
        self.assertTrue('title="my wonderful title"' in result)

    def test_image_tag_with_filters(self):
        result = self.render_image_tag_with_filters(self.image)
        self.assertTrue('width="200"' in result)
        self.assertTrue('height="100"' in result)

    def test_image_tag_with_chained_filters(self):
        result = self.render_image_tag(self.image, 'width-200 height-100')
        self.assertTrue('width="200"' in result)
        self.assertTrue('height="100"' in result)

    def test_filter_specs_must_match_allowed_pattern(self):
        with self.assertRaises(template.TemplateSyntaxError):
            self.render_image_tag(self.image, 'width-200x200|height-150')

        with self.assertRaises(template.TemplateSyntaxError):
            self.render_image_tag(self.image, 'width-200 alt"test"')

    def test_context_may_only_contain_one_argument(self):
        with self.assertRaises(template.TemplateSyntaxError):
            temp = template.Template(
                '{% load images_tags %}{% image image_obj width-200'
                ' as test_img this_one_should_not_be_there %}<img {{ test_img.attrs }} />'
            )
            context = template.Context({'image_obj': self.image})
            temp.render(context)

    def test_no_image_filter_provided(self):
        # if image template gets the image but no filters
        with self.assertRaises(template.TemplateSyntaxError):
            temp = template.Template(
                '{% load images_tags %}{% image image_obj %}'
            )
            context = template.Context({'image_obj': self.image})
            temp.render(context)

    def test_no_image_filter_provided_when_using_as(self):
        # if image template gets the image but no filters
        with self.assertRaises(template.TemplateSyntaxError):
            temp = template.Template(
                '{% load images_tags %}{% image image_obj as foo %}'
            )
            context = template.Context({'image_obj': self.image})
            temp.render(context)

    def test_no_image_attributes_allowed_when_using_as(self):
        # if image attrs used with the as variable
        with self.assertRaises(template.TemplateSyntaxError):
            temp = template.Template(
                '{% load images_tags %}{% image image_obj class="cover-image" as img %}'
            )
            context = template.Context({'image_obj': self.image})
            temp.render(context)

    def test_no_image_context_variable_when_using_as(self):
        # if image template gets the as but no variable name
        with self.assertRaises(template.TemplateSyntaxError):
            temp = template.Template(
                '{% load images_tags %}{% image image_obj as %}'
            )
            context = template.Context({'image_obj': self.image})
            temp.render(context)

    def test_no_image_filter_provided_but_attributes_provided(self):
        # if image template gets the image but no filters
        with self.assertRaises(template.TemplateSyntaxError):
            temp = template.Template(
                '{% load images_tags %}{% image image_obj class="cover-image" %}'
            )
            context = template.Context({'image_obj': self.image})
            temp.render(context)
