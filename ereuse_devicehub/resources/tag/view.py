from flask import Response, current_app as app, g, redirect, request
from flask_sqlalchemy import Pagination
from teal.marshmallow import ValidationError
from teal.resource import View, url_for_resource

from ereuse_devicehub.db import db
from ereuse_devicehub.query import things_response
from ereuse_devicehub.resources.device.models import Device
from ereuse_devicehub.resources.tag import Tag


class TagView(View):
    def post(self):
        """Creates a tag."""
        num = request.args.get('num', type=int)
        if num:
            res = self._create_many_regular_tags(num)
        else:
            res = self._post_one()
        return res

    def find(self, args: dict):
        tags = Tag.query.filter(Tag.is_printable_q()) \
            .order_by(Tag.created.desc()) \
            .paginate(per_page=200)  # type: Pagination
        return things_response(
            self.schema.dump(tags.items, many=True, nested=0),
            tags.page, tags.per_page, tags.total, tags.prev_num, tags.next_num
        )

    def _create_many_regular_tags(self, num: int):
        tags_id, _ = g.tag_provider.post('/', {}, query=[('num', num)])
        tags = [Tag(id=tag_id, provider=g.inventory.tag_provider) for tag_id in tags_id]
        db.session.add_all(tags)
        db.session().final_flush()
        response = things_response(self.schema.dump(tags, many=True, nested=1), code=201)
        db.session.commit()
        return response

    def _post_one(self):
        # todo do we use this?
        t = request.get_json()
        tag = Tag(**t)
        if tag.like_etag():
            raise CannotCreateETag(tag.id)
        db.session.add(tag)
        db.session().final_flush()
        db.session.commit()
        return Response(status=201)


class TagDeviceView(View):
    """Endpoints to work with the device of the tag; /tags/23/device"""

    def one(self, id):
        """Gets the device from the tag."""
        tag = Tag.from_an_id(id).one()  # type: Tag
        if not tag.device:
            raise TagNotLinked(tag.id)
        if not request.authorization:
            return redirect(location=url_for_resource(Device, tag.device.id))
        return app.resources[Device.t].schema.jsonify(tag.device)

    # noinspection PyMethodOverriding
    def put(self, tag_id: str, device_id: str):
        """Links an existing tag with a device."""
        tag = Tag.from_an_id(tag_id).one()  # type: Tag
        if tag.device_id:
            if tag.device_id == device_id:
                return Response(status=204)
            else:
                raise LinkedToAnotherDevice(tag.device_id)
        else:
            tag.device_id = device_id
        db.session().final_flush()
        db.session.commit()
        return Response(status=204)


def get_device_from_tag(id: str):
    """
    Gets the device by passing a tag id.

    Example: /tags/23/device.

    :raise MultipleTagsPerId: More than one tag per Id. Please, use
           the /tags/<organization>/<id>/device URL to disambiguate.
    """
    # todo this could be more efficient by Device.query... join with tag
    device = Tag.query.filter_by(id=id).one().device
    if not request.authorization:
        return redirect(location=url_for_resource(Device, device.id))
    if device is None:
        raise TagNotLinked(id)
    return app.resources[Device.t].schema.jsonify(device)


class TagNotLinked(ValidationError):
    def __init__(self, id):
        message = 'The tag {} is not linked to a device.'.format(id)
        super().__init__(message, field_names=['device'])


class CannotCreateETag(ValidationError):
    def __init__(self, id: str):
        message = 'Only sysadmin can create an eReuse.org Tag ({})'.format(id)
        super().__init__(message)


class LinkedToAnotherDevice(ValidationError):
    def __init__(self, device_id: int):
        message = 'The tag is already linked to device {}'.format(device_id)
        super().__init__(message)
