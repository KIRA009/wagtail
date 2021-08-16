from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from wagtail.admin import widgets
from wagtail.core import hooks
from wagtail.images.views.bulk_actions.image_bulk_action import ImageBulkAction


class TagForm(forms.Form):
    tags = forms.Field(widget=widgets.AdminTagWidget)


class AddTagsBulkAction(ImageBulkAction):
    display_name = _("Tag")
    action_type = "add_tags"
    aria_label = _("Add tags to images")
    template_name = "wagtailimages/bulk_actions/confirm_bulk_add_tags.html"
    action_priority = 20
    form_class = TagForm

    def check_perm(self, image):
        return self.permission_policy.user_has_permission_for_instance(self.request.user, 'change', image)

    def get_execution_context(self):
        return {
            'tags': self.cleaned_form.cleaned_data['tags'].split(',')
        }

    @classmethod
    def execute_action(cls, images, tags=[]):
        if not tags:
            return
        for image in images:
            cls.num_parent_objects += 1
            image.tags.add(*tags)

    def get_success_message(self):
        return ngettext(
            "New tags have been added to %(num_parent_objects)d image",
            "New tags have been added to %(num_parent_objects)d images",
            self.num_parent_objects
        ) % {
            'num_parent_objects': self.num_parent_objects
        }


@hooks.register('register_image_bulk_action')
def add_tags(request):
    return AddTagsBulkAction(request)
