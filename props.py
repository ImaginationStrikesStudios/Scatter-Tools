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


def update_axis(self, context):
    C_Slots = context.scene.C_Slots_settings
    Terrain = C_Slots.Terrain_pointer

    # list of all scatter particle system on terrain
    scatter_particles = [
        p for p in Terrain.modifiers if p.name[:7] == 'SCATTER']
    scatter_selected = [
        p for p in scatter_particles if p.particle_system.settings.scatter.p_selected]  # selected

    for sys in scatter_selected:
        for obj in sys.particle_system.settings.instance_collection.objects:
            obj.track_axis = self.axis


class ScatterToolsBatch(bpy.types.PropertyGroup):
    axis: bpy.props.EnumProperty(items=[("POS_X", "+X", "", 0),
                                        ("POS_Y", "+Y", "", 1),
                                        ("POS_Z", "+Z", "", 2),
                                        ("NEG_X", "-X", "", 3),
                                        ("NEG_Y", "-Y", "", 4),
                                        ("NEG_Z", "-Z", "", 5)], name="Batch Axis", update=update_axis)


def register():
    bpy.utils.register_class(ScatterToolsBatch)
    bpy.types.Scene.ScatterToolsBatch = bpy.props.PointerProperty(
        type=ScatterToolsBatch)


def unregister():
    bpy.utils.unregister_class(ScatterToolsBatch)
    del bpy.types.Scene.ScatterToolsBatch
