# -*- coding: utf-8 -*-
"""Tile Assembler Plugin using ffmpeg."""
import os

from System.IO import Path

from Deadline.Plugins import DeadlinePlugin
from Deadline.Scripting import (
    FileUtils, RepositoryUtils, SystemUtils)


def GetDeadlinePlugin():
    return PypeTileAssembler()


def CleanupDeadlinePlugin(deadlinePlugin):
    deadlinePlugin.cleanup()


class PypeTileAssembler(DeadlinePlugin):

    def __init__(self):
        self.InitializeProcessCallback += self.initialize_process
        self.RenderExecutableCallback += self.render_executable
        self.RenderArgumentCallback += self.render_argument
        self.PreRenderTasksCallback += self.pre_render_tasks
        self.PostRenderTasksCallback += self.post_render_tasks

    def cleanup(self):
        for stdoutHandler in self.StdoutHandlers:
            del stdoutHandler.HandleCallback

        del self.InitializeProcessCallback
        del self.RenderExecutableCallback
        del self.RenderArgumentCallback
        del self.PreRenderTasksCallback
        del self.PostRenderTasksCallback

    def initialize_process(self):
        self.SingleFramesOnly = True
        self.StdoutHandling = True

        self.AddStdoutHandlerCallback(
            ".*Error.*").HandleCallback += self.handle_stdout_error

    def render_executable(self):
        ffmpeg_exe_list = self.GetConfigEntry("FFmpeg_RenderExecutable")
        ffmpeg_exe = FileUtils.SearchFileList(ffmpeg_exe_list)

        if ffmpeg_exe == "":
            self.FailRender(("No file found in the semicolon separated "
                             "list \"{}\". The path to the render executable "
                             "can be configured from the Plugin Configuration "
                             "in the Deadline Monitor.").format(
                                ffmpeg_exe_list))

        return ffmpeg_exe

    def render_argument(self):

        output_file = self.GetPluginInfoEntryWithDefault("OutputFile", "")
        output_file = RepositoryUtils.CheckPathMapping(output_file)
        output_file = self.process_path(output_file)

        data = {}
        with open(self.config_file, "rU") as f:
            for text in f:
                # Parsing key-value pair and removing white-space
                # around the entries
                info = [x.strip() for x in text.split("=", 1)]

                if len(info) > 1:
                    try:
                        data[str(info[0])] = info[1]
                    except Exception as e:
                        # should never be called
                        print("Failed: {}".format(e))

        tile_info = []
        for tile in range(info["TileCount"]):
            tile_info.append({
                "filepath": info["Tile{}FileName"],
                "pos_x": info["Tile{}X"],
                "pos_y": info["Tile{}Y"]
            })

        ffmpeg_arguments = self.tile_completer_ffmpeg_args(
            info["ImageWidth"], info["ImageHeight"], tile_info, output_file)
        return "".join(ffmpeg_arguments)

    def process_path(self, filepath):
        if SystemUtils.IsRunningOnWindows():
            filepath = filepath.replace("/", "\\")
            if filepath.startswith("\\") and not filepath.startswith("\\\\"):
                filepath = "\\" + filepath
        else:
            filepath = filepath.replace("\\", "/")
        return filepath

    def pre_render_tasks(self):
        """Load config file and do remapping."""
        self.LogInfo("Pype Tile Assembler starting...")
        scene_filename = self.GetDataFilename()

        temp_scene_directory = self.CreateTempDirectory(
            "thread" + str(self.GetThreadNumber()))
        temp_scene_filename = Path.GetFileName(scene_filename)
        self.config_file = Path.Combine(
            temp_scene_directory, temp_scene_filename)

        if SystemUtils.IsRunningOnWindows():
            RepositoryUtils.CheckPathMappingInFileAndReplaceSeparator(
                scene_filename, self.config_file, "/", "\\")
        else:
            RepositoryUtils.CheckPathMappingInFileAndReplaceSeparator(
                scene_filename, self.config_file, "\\", "/")
            os.chmod(self.config_file, os.stat(self.config_file).st_mode)

    def post_render_tasks(self):
        self.LogInfo("Pype Tile Assembler Job finished.")

    def handle_stdout_error(self):
        self.FailRender(self.GetRegexMatch(0))

    def tile_completer_ffmpeg_args(
            self, output_width, output_height, tiles_info, output_path):
        """Generate fmpeg arguments for tile concatenation.

        Expected inputs are tiled images.

        Args:
            output_width (int): Width of output image.
            output_height (int): Height of output image.
            tiles_info (list): List of tile items, each item must be modifiable
                dictionary with `filepath`, `pos_x` and `pos_y` keys
                representing path to file and x, y coordinates on output
                image where top-left point of tile item should start.
            output_path (str): Path to file where should be output stored.

        Returns:
            (list): ffmpeg arguments.

        """
        previous_name = "base"
        ffmpeg_args = []
        filter_complex_strs = []

        filter_complex_strs.append("nullsrc=size={}x{}[{}]".format(
            output_width, output_height, previous_name
        ))

        new_tiles_info = {}
        for idx, tile_info in enumerate(tiles_info):
            # Add input and store input index
            filepath = tile_info["filepath"]
            ffmpeg_args.append("-i \"{}\"".format(filepath.replace("\\", "/")))

            # Prepare initial filter complex arguments
            index_name = "input{}".format(idx)
            filter_complex_strs.append(
                "[{}]setpts=PTS-STARTPTS[{}]".format(idx, index_name)
            )
            tile_info["index"] = idx
            new_tiles_info[index_name] = tile_info

        # Set frames to 1
        ffmpeg_args.append("-frames 1")

        # Concatenation filter complex arguments
        global_index = 1
        total_index = len(new_tiles_info)
        for index_name, tile_info in new_tiles_info.items():
            item_str = (
                "[{previous_name}][{index_name}]overlay={pos_x}:{pos_y}"
            ).format(
                previous_name=previous_name,
                index_name=index_name,
                pos_x=tile_info["pos_x"],
                pos_y=tile_info["pos_y"]
            )
            new_previous = "tmp{}".format(global_index)
            if global_index != total_index:
                item_str += "[{}]".format(new_previous)
            filter_complex_strs.append(item_str)
            previous_name = new_previous
            global_index += 1

        joined_parts = ";".join(filter_complex_strs)
        filter_complex_str = "-filter_complex \"{}\"".format(joined_parts)

        ffmpeg_args.append(filter_complex_str)
        ffmpeg_args.append("-y")
        ffmpeg_args.append("\"{}\"".format(output_path))

        return ffmpeg_args
