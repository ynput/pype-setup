# -*- coding: utf-8 -*-
"""Tile Assembler Plugin using Open Image IO tool.

Todo:
    Currently we support only EXRs with their data window set.
"""
import os

from System.IO import Path

from Deadline.Plugins import DeadlinePlugin
from Deadline.Scripting import (
    FileUtils, RepositoryUtils, SystemUtils)


def GetDeadlinePlugin():  # noqa: N802
    """Helper."""
    return PypeTileAssembler()


def CleanupDeadlinePlugin(deadlinePlugin):  # noqa: N802, N803
    """Helper."""
    deadlinePlugin.cleanup()


class PypeTileAssembler(DeadlinePlugin):
    """Deadline plugin for assembling tiles using OIIO."""

    def __init__(self):
        """Init."""
        self.InitializeProcessCallback += self.initialize_process
        self.RenderExecutableCallback += self.render_executable
        self.RenderArgumentCallback += self.render_argument
        self.PreRenderTasksCallback += self.pre_render_tasks
        self.PostRenderTasksCallback += self.post_render_tasks

    def cleanup(self):
        """Cleanup function."""
        for stdoutHandler in self.StdoutHandlers:
            del stdoutHandler.HandleCallback

        del self.InitializeProcessCallback
        del self.RenderExecutableCallback
        del self.RenderArgumentCallback
        del self.PreRenderTasksCallback
        del self.PostRenderTasksCallback

    def initialize_process(self):
        """Initialization."""
        self.SingleFramesOnly = True
        self.StdoutHandling = True

        self.AddStdoutHandlerCallback(
            ".*Error.*").HandleCallback += self.handle_stdout_error

    def render_executable(self):
        """Get render executable name.

        Get paths from plugin configuration, find executable and return it.

        Returns:
            (str): Render executable.

        """
        oiiotool_exe_list = self.GetConfigEntry("OIIOTool_RenderExecutable")
        oiiotool_exe = FileUtils.SearchFileList(oiiotool_exe_list)

        if oiiotool_exe == "":
            self.FailRender(("No file found in the semicolon separated "
                             "list \"{}\". The path to the render executable "
                             "can be configured from the Plugin Configuration "
                             "in the Deadline Monitor.").format(
                                oiiotool_exe_list))

        return oiiotool_exe

    def render_argument(self):
        """Generate command line arguments for render executable.

        Returns:
            (str): arguments to add to render executable.

        """
        # Read tile config file. This file is in compatible format with
        # Draft Tile Assembler
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
                        self.FailRender(
                            "Cannot parse config file: {}".format(e))

        # Get output file. We support only EXRs now.
        output_file = data["ImageFileName"]
        output_file = RepositoryUtils.CheckPathMapping(output_file)
        output_file = self.process_path(output_file)
        _, ext = os.path.splitext(output_file)
        if "exr" not in ext:
            self.FailRender(
                "[{}] Only EXR format is supported for now.".format(ext))

        tile_info = []
        for tile in range(int(data["TileCount"])):
            tile_info.append({
                "filepath": data["Tile{}".format(tile)],
                "pos_x": int(data["Tile{}X".format(tile)]),
                "pos_y": int(data["Tile{}Y".format(tile)])
            })

        # FFMpeg doesn't support tile coordinates at the moment.
        # arguments = self.tile_completer_ffmpeg_args(
        #     int(data["ImageWidth"]), int(data["ImageHeight"]),
        #     tile_info, output_file)

        arguments = self.tile_oiio_args(tile_info, output_file)
        self.LogInfo(
            "Using arguments: {}".format(" ".join(arguments)))
        return " ".join(arguments)

    def process_path(self, filepath):
        """Handle slashes in file paths."""
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
        """Print job finished."""
        self.LogInfo("Pype Tile Assembler Job finished.")

    def handle_stdout_error(self):
        """Handle errors in stdout."""
        self.FailRender(self.GetRegexMatch(0))

    def tile_oiio_args(self, tile_info, output_path):
        """Generate oiio tool arguments for tile assembly.

        Args:
            tiles_info (list): List of tile items, each item must be
                dictionary with `filepath`, `pos_x` and `pos_y` keys
                representing path to file and x, y coordinates on output
                image where top-left point of tile item should start.
            output_path (str): Path to file where should be output stored.

        Returns:
            (list): oiio tools arguments.

        """
        tile_paths_count = len(tile_info)
        args = []
        for idx, tile in enumerate(tile_info):
            args.append(tile["filepath"])
            if idx < tile_paths_count - 1:
                args.append("--add:mergeroi=1")

        args.append("-o")
        args.append(output_path)

        return args

    def tile_completer_ffmpeg_args(
            self, output_width, output_height, tiles_info, output_path):
        """Generate ffmpeg arguments for tile assembly.

        Expected inputs are tiled images.

        Args:
            output_width (int): Width of output image.
            output_height (int): Height of output image.
            tiles_info (list): List of tile items, each item must be
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
