from wagtail.admin.views.bulk_action import BulkAction
from wagtail.images import get_image_model
from wagtail.images.permissions import permission_policy as images_permission_policy


class ImageBulkAction(BulkAction):
    permission_policy = images_permission_policy
    models = [get_image_model()]

    def get_all_objects_in_listing_query(self, parent_id):
        _objects = self.model.objects.all()
        if parent_id is not None:
            _objects = _objects.filter(collection_id=parent_id)

        if 'q' in self.request.GET:
            query_string = self.request.GET.get('q', '')
            _objects = _objects.search(query_string).results()

        listing_objects = []
        for obj in _objects:
            listing_objects.append(obj.pk)

        return listing_objects

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['items_with_no_access'] = [
            {
                'item': image,
                'can_edit': self.permission_policy.user_has_permission_for_instance(self.request.user, 'change', image)
            } for image in context['items_with_no_access']
        ]
        return context
