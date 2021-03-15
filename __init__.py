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
import random

from . import prefs, props

bl_info = {
    "name": "Scatter tools",
    "author": "Reston Stanton",
    "description": "",
    "blender": (2, 92, 0),
    "version": (0, 1, 0),
    "location": "",
    "warning": "",
    "category": "Generic"
}

### START true terrian pro code ###


def particles_PreviewPicker(self, col, wm, iconType, addText):
    col.template_icon_view(wm, iconType, show_labels=True)
    row = col.row(align=True)
    row.alignment = 'CENTER'
    row.label(text=getattr(wm, iconType).replace('_', ' '))
    row = col.row()
    row.scale_y = 1.5
    row.operator('terrain.add_particles', text='Add '+addText, icon='ADD')


def particlesPanel(self, context, settings, wm, layout):
    # Particle type
    layout.separator()

    box = layout.box()
    col = box.column(align=True)
    row = col.row(align=True)
    #row.scale_y = 0.8
    row.prop(settings, 'particleObjectType', expand=True)

    # Particle Picker
    if settings.particleObjectType == 'ROCK':
        particles_PreviewPicker(
            self, col, wm, 'particle_rock_icons', 'Rocks')
    elif settings.particleObjectType == 'TREE':
        row = col.row(align=True)
        row.prop(settings, 'particleTreeRes', expand=True)
        particles_PreviewPicker(
            self, col, wm, 'particle_tree_icons', 'Trees')
    elif settings.particleObjectType == 'GRASS':
        particles_PreviewPicker(
            self, col, wm, 'particle_grass_icons', 'Grass')


def True_Terrian_draw(self, context, layout):
    settings = bpy.context.scene.terrain_settings
    wm = context.window_manager

    particlesPanel(self, context, settings, wm, layout)

### START sort algorithm ###


def swap(L, i):
    temp = L[i]
    L[i] = L[i + 1]
    L[i + 1] = temp


def one_bubble_name_pass(L):
    returnval = False
    for i in range(len(L)-1):
        if L[i].name > L[i+1].name:
            swap(L, i)
            returnval = True
    return returnval


def bubble_sort_name(L):
    flag = True
    while flag:
        flag = one_bubble_name_pass(L)
### END sort algorithm ###


def users_poll_filter(self, object):
    if object.users < 1:
        return False
    else:
        return True


class Props(bpy.types.PropertyGroup):
    sys: bpy.props.PointerProperty(
        type=bpy.types.ParticleSettings, name="", poll=users_poll_filter)


class ConvertBotaniqOperator(bpy.types.Operator):
    bl_idname = "scatter_tools.convert_botaniq"
    bl_label = "convert"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        if not context.scene.ScatterTools.sys:
            self.report({"ERROR"}, "No particle system selected")
            return {"CANCELLED"}
        sys_name = context.scene.ScatterTools.sys.name
        context.scene.ScatterTools.sys = None

        # initial vars
        total = 0
        count = bpy.data.particles[sys_name].count
        total_list = []
        new_counts = []
        change_counts = []
        names = []

        similar_names = []
        collections = []

        sorted_instance_weights = bpy.data.particles[sys_name].instance_weights[:]
        bubble_sort_name(sorted_instance_weights)

        # get numbers from use count and object names
        for i in sorted_instance_weights:
            total += int(i.name[-2:])
            total_list.append(int(i.name[-2:]))
            c_name = i.name.split(": ")
            names.append(c_name[0])

        # get the new count per system
        split = round(count/total)
        for i in total_list:
            new_counts.append(i*split)

        # __DEBUG__ #
        print("\n\n")
        for i in range(len(names)):
            print(names[i], new_counts[i])

        # find smiler objects and remove all objects from the collection
        prev_name = None
        for i in range(len(names)):
            name_part = names[i].split("_")
            current_name = name_part[0] + "_" + name_part[1]
            if prev_name != None:
                if prev_name == current_name:
                    if new_counts[i] == new_counts[i-1]:
                        similar_names.append(prev_name)
                        # index, count, removeindex
                        change_counts.append([i, new_counts[i], i-1])

            prev_name = current_name
            obj = bpy.data.objects[names[i]]
            obj.users_collection[0].objects.unlink(obj)

        # remove bad counts from counts
        print("\n\n")
        print(change_counts)
        change_counts.reverse()
        print(change_counts)
        print(new_counts)
        for i in change_counts:
            new_counts[i[0]] += i[1]
            new_counts.pop(i[2])
            names.pop(i[2])
        print(new_counts)

        # __DEBUG__ #
        print("\n\n")
        for i in range(len(names)):
            print(names[i], new_counts[i])

        # loop throw smiler objects and add them to a group collection
        for i in similar_names:
            try:
                bpy.data.collections[i]
            except KeyError:
                coll = bpy.data.collections.new(name=i)
                collections.append(coll)
                context.scene.collection.children.link(coll)

            for j in names:
                if i in j:
                    try:
                        coll.objects.link(bpy.data.objects[j])
                    except RuntimeError:
                        continue

        # make all collections
        for i in names:
            obj = bpy.data.objects[i]
            if not obj.users_collection:
                coll = bpy.data.collections.new(name=i)
                coll.objects.link(obj)
                context.scene.collection.children.link(coll)
                collections.append(coll)

        print("\n")
        for i in collections:
            print(i.name)
        # sort collections
        bubble_sort_name(collections)
        print("\n")
        for i in collections:
            print(i.name)

        # add new systems with proper names, objects->Collections, and counts
        for i in range(len(collections)):
            bpy.ops.object.particle_system_add()
            context.object.particle_systems[context.object.particle_systems.active_index].settings = bpy.data.particles[sys_name].copy(
            )
            name = context.object.particle_systems.active_index
            context.object.particle_systems[name].name = collections[i].name
            context.object.particle_systems[name].seed = random.randrange(
                0, 1000000000)
            sys = context.object.particle_systems[name].settings
            sys.count = new_counts[i]  # fiX!!!!!!!!!!!!!!!!!!!!
            sys.render_type = "COLLECTION"
            sys.use_collection_count = False
            sys.instance_collection = collections[i]
            sys.name = collections[i].name
            # print(sys.name)
            bpy.ops.scatter.core_convert(
                "INVOKE_DEFAULT", psy=sys.name, is_gw=False)

        # remove old particle system
        mod_name = None
        mod_index = None
        obj = context.object
        for i in range(len(obj.modifiers)):
            mod = obj.modifiers[i]
            if mod.type == "PARTICLE_SYSTEM":
                if mod.particle_system.settings.name == sys_name:
                    mod_name = mod.name
                    mod_index = i
        context.object.particle_systems.active_index = mod_index
        bpy.ops.object.particle_system_remove()

        # rename collections
        for i in collections:
            print(i.name)
            print("      ", i.name)
            i.name = "SCATTER: " + i.name
            print("            ", coll.name)
        return {'FINISHED'}

        return {'FINISHED'}


class ConvertTrueOperator(bpy.types.Operator):
    bl_idname = "scatter_tools.convert_true"
    bl_label = "convert"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        sys_name = context.scene.ScatterTools.sys.name
        context.scene.ScatterTools.sys = None
        sys = bpy.data.particles[sys_name]
        coll = sys.instance_collection
        length = sys.hair_length
        sys.hair_length = length / length
        sys.particle_size = sys.particle_size * length
        bpy.ops.scatter.core_convert(
            "INVOKE_DEFAULT", psy=sys.name, is_gw=False)

        # rename collections
        for i in bpy.data.particles:
            print(i.name)
            if sys_name in i.name:
                print("      ", i.name)
                coll.name = "SCATTER: " + i.name
                print("            ", coll.name)
        return {'FINISHED'}


class CleanOperator(bpy.types.Operator):
    bl_idname = "scatter_tools.clean"
    bl_label = "clean"

    def execute(self, context):
        for i in bpy.data.particles:
            if i.users < 1:
                bpy.data.particles.remove(i)
        return {'FINISHED'}


class BoundsOperator(bpy.types.Operator):
    bl_idname = "scatter_tools_batch.bounds"
    bl_label = "Bounds Batch"

    set_true: bpy.props.BoolProperty(name="set true", default=True)

    def execute(self, context):
        C_Slots = context.scene.C_Slots_settings
        Terrain = C_Slots.Terrain_pointer

        # list of all scatter particle system on terrain
        scatter_particles = [
            p for p in Terrain.modifiers if p.name[:7] == 'SCATTER']
        scatter_selected = [
            p for p in scatter_particles if p.particle_system.settings.scatter.p_selected]  # selected

        for sys in scatter_selected:
            for obj in sys.particle_system.settings.instance_collection.objects:
                if self.set_true:
                    obj.display_type = 'BOUNDS'
                else:
                    obj.display_type = 'TEXTURED'

        return {'FINISHED'}


class VIEW_3D_PT_ScatterTools(bpy.types.Panel):
    bl_label = ""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "Scatter"
    bl_parent_id = "SCATTER_PT_creation"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        row = layout.row()
        row.label(icon="TOOL_SETTINGS", text="Scatter Tools")

    def draw(self, context):
        preferences = prefs.get_preferences()

        ### Botaniq ###
        if preferences.botaniq:
            layout = self.layout.box()

            layout.label(text="Botaniq")

            layout.emboss = "PULLDOWN_MENU"
            col = layout.column()
            col.scale_y = 2
            col.operator("botaniq.scatter_assets", text="Scatter Botaniq Biomes",
                         icon="OUTLINER_OB_GROUP_INSTANCE")

            layout.emboss = "NORMAL"
            col = layout.column()
            # col.separator()
            col.prop(context.scene.ScatterTools, "sys")

            layout.emboss = "PULLDOWN_MENU"
            col = layout.column()
            col.scale_y = 2
            col.operator("scatter_tools.convert_botaniq", icon="FILE_REFRESH")

            col = layout.column()
            # col.separator()
            col.operator("scatter_tools.clean", icon="BRUSH_DATA")

        ### True Grass ###
        if preferences.true_grass:
            layout = self.layout.box()

            layout.label(text="True Grass")

            layout.emboss = "PULLDOWN_MENU"
            col = layout.column()
            col.popover(panel="VIEW3D_PT_true_grass",
                        icon="OUTLINER_OB_GROUP_INSTANCE", text="True Grass", )

            layout.emboss = "NORMAL"
            col = layout.column()
            col.prop(context.scene.ScatterTools, "sys")
            layout.emboss = "PULLDOWN_MENU"
            col = layout.column()
            col.scale_y = 2
            col.operator("scatter_tools.convert_true")

            col = layout.column()
            # col.separator()
            col.operator("scatter_tools.clean", icon="BRUSH_DATA")

        ### True Terrian ###
        if preferences.true_terrian:
            layout = self.layout.box()

            layout.label(text="True Terrain")

            layout.emboss = "NORMAL"
            col = layout.column()

            True_Terrian_draw(self, context, layout)

            layout.emboss = "NORMAL"
            col = layout.column()
            col.prop(context.scene.ScatterTools, "sys")
            layout.emboss = "PULLDOWN_MENU"
            col = layout.column()
            col.scale_y = 2
            col.operator("scatter_tools.convert_true")

            col = layout.column()
            # col.separator()
            col.operator("scatter_tools.clean", icon="BRUSH_DATA")

        if not preferences.botaniq and not preferences.true_terrian and not preferences.true_grass:
            self.layout.label(text="No Conversion Set", icon="ERROR")
            self.layout.label(text="Enable them in the addon prefrances")


class VIEW_3D_PT_ScatterToolsBatch(bpy.types.Panel):
    bl_label = ""
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = "objectmode"
    bl_category = "Scatter"
    bl_parent_id = "SCATTER_PT_tweaking"
    bl_options = {"DEFAULT_CLOSED"}

    def draw_header(self, context):
        layout = self.layout
        row = layout.row()
        row.label(icon="TOOL_SETTINGS", text="Scatter Tools Batch")

    def draw(self, context):
        batch_settings = context.scene.ScatterToolsBatch
        layout = self.layout
        row = layout.row()
        row.prop(batch_settings, "axis")

        row = layout.row(align=True)

        settings = row.operator("scatter_tools_batch.bounds",
                                icon="CUBE", text="Set Bounds")
        settings.set_true = True

        settings = row.operator(
            "scatter_tools_batch.bounds", icon="CUBE", text="Set Solid")
        settings.set_true = False


classes = (VIEW_3D_PT_ScatterTools, VIEW_3D_PT_ScatterToolsBatch, Props,
           ConvertBotaniqOperator, ConvertTrueOperator, CleanOperator, BoundsOperator)


def register():
    props.register()
    for i in classes:
        bpy.utils.register_class(i)
    prefs.register()
    bpy.types.Scene.ScatterTools = bpy.props.PointerProperty(type=Props)


def unregister():
    props.unregister()
    for i in classes:
        bpy.utils.unregister_class(i)
    prefs.unregister()
    del bpy.types.Scene.ScatterTools
