import json
from django.utils.translation import ugettext
import pkg_resources

from django.template import Template, Context

from xblock.core import XBlock
from xblock.exceptions import JsonHandlerError
from xblock.fields import Scope, String, Integer, Float, Boolean, List, DateTime, JSONField
from xblock.fragment import Fragment
from xblock.validation import Validation
from xblockutils.studio_editable import StudioEditableXBlockMixin, FutureFields
from xmodule.x_module import XModuleMixin


@XBlock.needs('user')
class JupyterhubXBlock(StudioEditableXBlockMixin, XBlock):

    display_name = String(
        display_name="Display Name",
        help="Display name for this module",
        default="Jupyterhub",
        scope=Scope.settings,
    )

    url_resource = String(
        scope=Scope.settings
    )

    file_noteBook = String(
        display_name="Upload file noteBook",
        scope=Scope.settings,
        resettable_editor=False
    )

    editable_fields = ('display_name', 'file_noteBook')

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    def studio_view(self, context):
        """
        Render a form for editing this XBlock
        """
        fragment = Fragment()
        context = {'fields': [],
                   'courseKey': self.location.course_key}
        # Build a list of all the fields that can be edited:
        for field_name in self.editable_fields:
            field = self.fields[field_name]
            assert field.scope in (Scope.content, Scope.settings), (
                "Only Scope.content or Scope.settings fields can be used with "
                "StudioEditableXBlockMixin. Other scopes are for user-specific data and are "
                "not generally created/configured by content authors in Studio."
            )
            field_info = self._make_field_info(field_name, field)
            if field_info is not None:
                context["fields"].append(field_info)
        fragment.content = self.render_template('static/html/studio_edit.html', context)
        fragment.add_css(self.resource_string("static/css/jupyterhub_xblock.css"))
        fragment.add_javascript(self.resource_string("static/js/src/studio_edit.js"))
        fragment.initialize_js('JupyterhubStudioEditableXBlock')
        return fragment

    def student_view(self, context=None):
        context = {
            'self': self,
            'user_is_staff': self.runtime.user_is_staff,
            'current_url_resource': self.get_current_url_resource()
        }
        template = self.render_template("static/html/jupyterhub_xblock.html", context)
        frag = Fragment(template)
        frag.add_css(self.resource_string("static/css/jupyterhub_xblock.css"))
        frag.add_javascript(self.resource_string("static/js/src/jupyterhub_xblock.js"))
        frag.initialize_js('JupyterhubXBlock')
        return frag

    def get_current_url_resource(self):
        return 'http://127.0.0.1:8880/user/name/tree'

    def render_template(self, template_path, context):
        template_str = self.resource_string(template_path)
        template = Template(template_str)
        return template.render(Context(context))

    def _make_field_info(self, field_name, field):
        info = super(JupyterhubXBlock, self)._make_field_info(field_name, field)
        if field_name == 'file_noteBook':
            info['type'] = 'file_uploader'
        return info

    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("JupyterhubXBlock",
             """<vertical_demo>
                <jupyterhub_xblock/>
                </vertical_demo>
             """),
        ]
