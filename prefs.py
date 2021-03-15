# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import bpy


def get_preferences():
    return bpy.context.preferences.addons[__package__].preferences


class Default(bpy.types.AddonPreferences):
    bl_idname = __package__

    botaniq: bpy.props.BoolProperty(
        name="Botaniq",
        description="Enabled Botaniq Conversion",
        default=True)

    true_terrian: bpy.props.BoolProperty(
        name="True Terrain",
        description="Enabled True Terrain Conversion",
        default=True)

    true_grass: bpy.props.BoolProperty(
        name="True Grass",
        description="Enabled True Grass Conversion",
        default=True)

    def draw(self, context):
        layout = self.layout

        row = layout.row()
        row.prop(self, "botaniq")
        row.prop(self, "true_terrian")
        row.prop(self, "true_grass")

        # row.separator(factor=5)


def register():
    bpy.utils.register_class(Default)


def unregister():
    bpy.utils.unregister_class(Default)
