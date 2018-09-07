# pype.club - avalon-app roadmap
<!--

Integrations template:

### Application:
_Short introduction of an application, usually taken from its official website._
> **Links**:
[website](https://official-website-address.domane),
# also any link to anything usefull which would be important to know for develpers to work with as initialisation.

</br>
> **Supported version**: what version its supported from </br>
> **Features**:
[`feature`](#feat),
# list all the features planned of available for the application. Also make sure the feature is listed in "List of Avalon integraton tools". Then put longer description of the feature in section "Integration tools" with working link.

</br>
> **Repository**:
[pypeclub](https://github.com/pypeclub) /
[avalon-nuke](https://github.com/pypeclub/avalon-nuke) </br>
> **Release date**: winter 2018 </br>

-->
## List of integrations we are planning to work on:
1. [Production softwares:](#1)
 - Autodesk - Maya
 - SideFX - Houdini
 - Foundry - Nuke / NukeAssist / NukeStudio / Hiero / HieroPlayer
 - Blackmagic - DaVinci Resolve / Fusion
 - Adobe - Photoshop, AfterEffects
 - Blender
2. [Review:](#2)
 - RV
 - DjV
3. [Render farm management:](#3)
 - Deadline
 - RoyalRender
4. [Production management solutions:](#4)
 - Ftrack
 - Shotgun
 - CG Wire
5. [Studio asset management:](#5)
 - research needed
 - feature request bellow
6. [Production planning solution:](#6)
 - research needed
 - feature request bellow

****
## List of Avalon integration tools ([details](#integrators)):
   - [`Wrapper`](#wrapper) - sets environment | app menu with actions | link to studio tool repository
   - [`Project manager (gui)`](#project) - stand-alone or in an app interface for setting/altering basic attributes of project
   - [`Template Manager (gui)`](#template) - interface for management of folder structure, name conventions and data & colorspace workflow definitions of each project also it is great place for definition of project schema
   - [`Publisher (gui)`](#publish) - interface (Pyblish) for publishing of task submitions for review and following job inputs.
   - [`Asset browser/loader (gui)`](#asset_load) - interface for browsing and loading available assets into a working scene or script.
   - [`Asset create (gui)`](#asset_create) - tool for creating a new asset from working scene or script
   - [`Workfiles (gui)`](#workfile) - interface for selecting or versioning working files
   - [`Instance Creator (gui)`](#instance) - tool for creating instance from selected object in a scene or script
   - [`Container Manager (gui)`](#container) - tool for visualising of loaded assets and its versions in a scene or script. This tool can be used for checking/changing version of assets
   - [`Job submiter`](#submiter) - submits job on to a render farm, producion hooks could be mounted before or after render actions
   - [`DB sync`](#db-sync) - pulling pushing of databases on demand
   - [`Locations sync`](#loc-sync) - a serve hook for synchronization of project file storage location between avalon and other [production planning solutions](#6)
   - [`Launcher convert`](#launch-action) - dynamic hook which converts avalon's launchers onto any used [production planning solution](#6) actions for its front-end software launching
   - [`Event server`](#eserver) - production server runnig actions regarding available context of defined hooks
   - [`Hooks`](#hooks) - custom hooks

****
## 1. Production softwares: <a name="1"></a>
### Maya:
_Maya® 3D animation, modeling, simulation, and rendering software provides an integrated, powerful toolset. Use it for animation, environments, motion graphics, virtual reality, and character creation._
> **Links**: [Overview](https://www.autodesk.eu/products/maya/overview)</br>
> **Supported version**: 2016 and newer </br>
> **Features**:
[`Wrapper`](#wrapper),
[`Publisher (gui)`](#publish),
[`Asset browser/loader (gui)`](#asset_load),
[`Workfiles (gui)`](#workfile),
[`Instance Creator (gui)`](#instance),
[`Container Manager (gui)`](#container),
</br>
> **Repository**:
[pypeclub](https://github.com/pypeclub) /
[avalon-maya](https://github.com/pypeclub/avalon-maya) </br>
> **Release date**: winter 2018 </br>

</br>

### Houdini:
_Houdini FX combines superior performance and dramatic, ease-of-use to deliver a powerful and accessible 3D experience to VFX artists creating feature films, commercials or video games_
> **Links**: [Houdini FX](https://www.sidefx.com/products/houdini-fx/)</br>
> **Supported version**: ??? </br>
> **Features**:
[`Wrapper`](#wrapper),
[`Publisher (gui)`](#publish),
[`Asset browser/loader (gui)`](#asset_load),
[`Workfiles (gui)`](#workfile),
[`Instance Creator (gui)`](#instance),
[`Container Manager (gui)`](#container),
</br>
> **Repository**:
[pypeclub](https://github.com/pypeclub) /
[avalon-houdini](https://github.com/pypeclub/avalon-houdini) </br>
> **Release date**: winter 2018 (basic), spring 2019 (extended)</br>

</br>

### Nuke/-x:
_Nuke®, NukeX® and Nuke Studio® offer cutting-edge toolkits for node-based compositing, editorial and review. The Nuke family's unparalleled flexibility and collaborative workflows help you get the highest quality results—fast._
> **Links**: [Overview](https://www.foundry.com/products/nuke)</br>
> **Supported version**: 10.5 and newer</br>
> **Features**:
[`Wrapper`](#wrapper),
[`Publisher (gui)`](#publish),
[`Asset browser/loader (gui)`](#asset_load),
[`Workfiles (gui)`](#workfile),
[`Instance Creator (gui)`](#instance),
</br>
> **Repository**:
[pypeclub](https://github.com/pypeclub) /
[avalon-nuke](https://github.com/pypeclub/avalon-nuke) </br>
> **Release date**: winter 2018 </br>

</br>

### NukeAssist:
_Nuke's spin for Roto and Paint only_
> **Links**: [Overview](https://www.foundry.com/products/nuke)</br>
> **Supported version**: 10.5 and newer</br>
> **Features**:
[`Wrapper`](#wrapper),
[`Publisher (gui)`](#publish),
[`Asset browser/loader (gui)`](#asset_load),
[`Workfiles (gui)`](#workfile),
</br>
> **Repository**:
[pypeclub](https://github.com/pypeclub) /
[avalon-nuke](https://github.com/pypeclub/avalon-nuke) </br>
> **Release date**: winter 2018 </br>

</br>

### Nuke Studio:
_Nuke®, NukeX® and Nuke Studio® offer cutting-edge toolkits for node-based compositing, editorial and review. The Nuke family's unparalleled flexibility and collaborative workflows help you get the highest quality results—fast._
> **Links**: [Overview](https://www.foundry.com/products/nuke)</br>
> **Supported version**: 10.5 and newer</br>
> **Features**:
[`Wrapper`](#wrapper),
[`Project manager (gui)`](#project),
[`Publisher (gui)`](#publish),
[`Asset create (gui)`](#asset_create)
[`Template Manager (gui)`](#template)
[`Asset browser/loader (gui)`](#asset_load),
[`Workfiles (gui)`](#workfile),
</br>
> **Repository**:
[pypeclub](https://github.com/pypeclub) /
[avalon-nuke](https://github.com/pypeclub/avalon-nuke) &
[avalon-hiero](https://github.com/pypeclub/avalon-hiero) </br>
> **Release date**: winter 2018 </br>

</br>

### Hiero:
_Hiero is part of the Nuke family, offering the same powerful multi-track editorial timeline as Nuke Studio. Producers, VFX editors, and coordinators get greater visibility over projects, while seamless timeline sharing with other Hiero seats, HieroPlayer and Nuke Studio reduces the need to reconform for review._
> **Links**: [Overview](https://www.foundry.com/products/hiero)</br>
> **Supported version**: 10.5 and newer</br>
> **Features**:
[`Wrapper`](#wrapper),
[`Project manager (gui)`](#project),
[`Publisher (gui)`](#publish),
[`Asset create (gui)`](#asset_create)
[`Template Manager (gui)`](#template)
[`Asset browser/loader (gui)`](#asset_load),
[`Workfiles (gui)`](#workfile),
 </br>
 > **Repository**:
 [pypeclub](https://github.com/pypeclub) /
 [avalon-hiero](https://github.com/pypeclub/avalon-hiero) </br>
> **Release date**: winter 2018 </br>

</br>

### DaVinci Resolve:
_The world’s first solution that combines professional offline and online editing, color correction, audio post production and now visual effects all in one software tool!_
> **Links**: [Overview](https://www.blackmagicdesign.com/products/davinciresolve/)</br>
> **Supported version**: 15 and newer </br>
> **Features**:
[`Wrapper`](#wrapper),
[`Project manager (gui)`](#project),
[`Publisher (gui)`](#publish),
[`Asset create (gui)`](#asset_create)
[`Template Manager (gui)`](#template)
[`Asset browser/loader (gui)`](#asset_load),
[`Workfiles (gui)`](#workfile),
</br>
> **Repository**:
[pypeclub](https://github.com/pypeclub) /
[avalon-resolve](https://github.com/pypeclub/avalon-resolve) </br>
> **Release date**: winter 2018 </br>

</br>

### Fusion:
_Short description of the software_
> **Links**: [link text](httls://thislink.domane)</br>
> **Supported version**: </br>
> **Features**:
[`Wrapper`](#wrapper),
[`Publisher (gui)`](#publish),
[`Asset browser/loader (gui)`](#asset_load),
[`Workfiles (gui)`](#workfile),
</br>
> **Repository**:
[pypeclub](https://github.com/pypeclub) /
[avalon-fusion](https://github.com/pypeclub/avalon-fusion) </br>
> **Release date**: winter 2018 </br>

</br>

### Photoshop:
_Short description of the software_
> **Links**: [link text](httls://thislink.domane)</br>
> **Supported version**: </br>
> **Features**:
[`Wrapper`](#wrapper),
[`Publisher (gui)`](#publish),
[`Asset browser/loader (gui)`](#asset_load),
`Workfiles (gui)`
</br>
> **Repository**:
[pypeclub](https://github.com/pypeclub) /
[avalon-photoshop](https://github.com/pypeclub/avalon-photoshop) </br>
> **Release date**: summer 2019 </br>

</br>

### AfterEffects:
_Short description of the software_
> **Links**: [link text](httls://thislink.domane)</br>
> **Supported version**: </br>
> **Features**:
[`Wrapper`](#wrapper),
[`Publisher (gui)`](#publish),
[`Asset browser/loader (gui)`](#asset_load),
[`Workfiles (gui)`](#workfile),
</br>
> **Repository**:
[pypeclub](https://github.com/pypeclub) /
[avalon-aftereffects](https://github.com/pypeclub/avalon-aftereffects) </br>
> **Release date**: summer 2019 </br>
</br>

### Blender
_Short description of the software_
> **Links**: [link text](httls://thislink.domane)</br>
> **Supported version**: </br>
> **Features**:
[`Wrapper`](#wrapper),
[`Project manager (gui)`](#project),
[`Publisher (gui)`](#publish),
[`Asset create (gui)`](#asset_create)
[`Template Manager (gui)`](#template)
[`Asset browser/loader (gui)`](#asset_load),
[`Workfiles (gui)`](#workfile),
[`Instance Creator (gui)`](#instance),
[`Container Manager (gui)`](#container),
</br>
> **Repository**:
[pypeclub](https://github.com/pypeclub) /
[avalon-blender](https://github.com/pypeclub/avalon-blender) </br>
> **Release date**: summer 2019 </br>

</br></br>

## 2. Review: <a name="2"></a>
### HieroPlayer:
_Short description of the software_
> **Links**: [link text](httls://thislink.domane)</br>
> **Supported version**: </br>
> **Features**:
[`Wrapper`](#wrapper),
[`Asset browser/loader (gui)`](#asset_load),
</br>
> **Repository**:
[pypeclub](https://github.com/pypeclub) /
[avalon-hiero](https://github.com/pypeclub/avalon-hiero) </br>
> **Release date**: winter 2018 </br>
</br>

### RV:
_RV is high performance professional playback and review application optimized for direct from disk and cached RAM playback. So, RV works everywhere from the desktop to the digital theater with SDI output._
> **Links**: [website](http://www.tweaksoftware.com/products/rv)</br>
> **Supported version**: ? </br>
> **Features**:
[`Wrapper`](#wrapper),
[`Asset browser/loader (gui)`](#asset_load)
</br>
> **Repository**:
[pypeclub](https://github.com/pypeclub) /
[avalon-rv](https://github.com/pypeclub/avalon-rv) </br>
> **Release date**: winter 2018 </br>
</br>

### DjV:
_Short description of the software_
> **Links**: [link text](httls://thislink.domane)</br>
> **Supported version**: </br>
> **Features**:
[`Wrapper`](#wrapper),
[`Asset browser/loader (gui)`](#asset_load)
</br>
> **Release date**: summer 2019 </br>

</br></br>

## 3. Render farm management: <a name="3"></a>
### Deadline:
_Deadline is a hassle-free administration and compute management toolkit for Windows, Linux, and Mac OSX based render farms, and supports over 80 different content creation applications out of the box._
> **Links**: [website](https://deadline.thinkboxsoftware.com/)</br>
> **Supported version**: ?</br>
> **Features**:
[`Job submiter`](#submiter)
</br>
> **Repository**:
[pypeclub](https://github.com/pypeclub) /
[avalon-deadline](https://github.com/pypeclub/avalon-deadline) </br>
> **Release date**: spring 2019 </br>

</br>

### RoyalRender:
_Royal Render is a mighty application to organize your render jobs. The high end tool to manage and control your renderings on Windows, Linux, and Mac OSX._
> **Links**: [website](http://www.royalrender.de)</br>
> **Supported version**: v7 and newer</br>
> **Features**:
[`Job submiter`](#submiter)
</br>
> **Repository**:
[pypeclub](https://github.com/pypeclub) /
[avalon-royalrender](https://github.com/pypeclub/avalon-royalrender) </br>
> **Release date**: winter 2018 </br>

</br></br>

## 4. Production management solutions: <a name="4"></a>
### Ftrack:
_Ftrack is a scalable cloud-based project management solution used in the media & entertainment industry to help teams meet the ever-increasing demands of post production._
> **Links**: [website](https://www.ftrack.com/en/)</br>
> **Supported version**: v3 and newer</br>
> **Features**:
[`DB sync`](#db-sync),
[`Locations sync`](#loc-sync),
[`Launcher convert`](#launch-action),
[`Event server`](#eserver),
[`Hooks`](#hooks)
</br>
> **Repository**:
[pypeclub](https://github.com/pypeclub) /
[avalon-ftrack](https://github.com/pypeclub/avalon-ftrack) </br>
> **Release date**: winter 2018 </br>

</br>

### Shotgun:
_Tools that connect entire studios, teams, and creative workflows._
> **Links**: [website](https://www.shotgunsoftware.com)</br>
> **Features**:
[`DB sync`](#db-sync),
[`Launcher convert`](#launch-action),
[`Event server`](#eserver),
[`Hooks`](#hooks)
</br>
> **Release date**: summer 2019 </br>

</br>

### CG Wire:
_CGWire is a production tracking solution aimed to provide services for small to mid-size studios. It enables you to dispatch tasks, send feedback and validate the work done._
> **Links**: [website](https://www.cg-wire.com/en)</br>
> **Features**:
[`DB sync`](#db-sync),
[`Launcher convert`](#launch-action),
[`Event server`](#eserver),
[`Hooks`](#hooks)
</br>
> **Release date**: winter 2018 </br>

</br></br>

## 5. Studio asset management: <a name="5"></a>
  - Inhouse server, mongodb, separate DB from Avalon
  - Easy to filter by catogory, keywoard, metadata. Like you are e-shoping on Alza.cz, you could even add it into basket and then process all together, or creat your preference lists :)
  - populating assets into the database by Pyblish from a software
  - data on file storage, human readable, metadata.json (toml)
  - web front-end with image thumbnails
  - each asset on front-end has copiable link which could be pasted into production software and it will add asset into the scene with correct matadata
  - *.abc, *.obj, *.exr, *.png, *.jpg, *.mov, materials, fonts
  - multiple quality versions
  - batch injest tool: simple rename and sort into folder structure will define database hiearchy. It will populate available metadata from file or metadata file in case it has the same name. If not superted file type it will auto convert into suported.
    - 2D assets batch convert using Nuke
    - 3D assets batch convert using Maya
  - solution could be [Jupyter Notebook](http://jupyter.org/) or [iPython](http://ipython.org/)
  - html canvas 3d object [Tree.js](https://manu.ninja/webgl-3d-model-viewer-using-three-js/)
  - great example of functionality! [blender addon](http://www.pitiwazou.com/asset_management/)

## 6. Production planning solution: <a name="6"></a>
- rewrite of the F.Maker tool from ML (Ondra.S.)
- should be dead simple and fast for work (perhaps Chrome extention app)
- should be able synchronize with avalon database, so project would be filled with camera metadata and ref images
- should be able to take pictures on set if in laptop and screengrab if on workstation
- it should be tool for prepro and budgetting
- simple ways of renaming shooting-day.shot.take and [shot].assets, [sequence].assets
- you should be able to do breakdown of vfx shot and as you sinchronize it with avalon.nukestudio it should add tasks onto the shot containers
- you should be able to do simple drawing and annotations on shots, storyboard
- you should be able to quickly sketch scheduling and do snapshot of it so you could do several versions and pehrhaps comment to identify
- it has to be able hold several workflow schema templates
- it would save to Google drive and sync whenever it would be possible
- synchronizable with `Storyboard Pro` of `Flix`
- able to preview story script with film strip vertically on side to see the flow, Technical script for directors made simple.
- should be colaborative
- [ChromeAppDev youtube intro](https://www.youtube.com/watch?v=f3NctLbtsNE&feature=youtu.be)

</br></br>

****
## Integration tools: <a name="integrators"></a>
### Wrapper: <a name="wrapper"></a>
sets environment | app menu with actions | link to studio tool repository

### Project manager (gui): <a name="project"></a>
stand-alone or in an app interface for setting/altering basic attributes of project

### Template Manager (gui): <a name="template"></a>
interface for management of folder structure, name conventions and data & colorspace workflow definitions of each project also it is great place for definition of project schema

### Publisher (gui): <a name="publish"></a>
interface (Pyblish) for publishing of task submitions for review and following job inputs.

### Asset browser/loader (gui): <a name="asset_load"></a>
interface for browsing and loading available assets into a working scene or script. It works either withing a project or studio resources. Filters by metadata. Adding to "sandbox" (is there better word for the function?) before importing to scene or script (import attributes: bool::handles,).

### Asset create (gui): <a name="asset_create"></a>
tool for creating a new asset from working scene or script

### Workfiles (gui): <a name="workfile"></a>
interface for selecting or versioning working files

### Instance Creator (gui): <a name="instance"></a>
description of the feature possibly with a picture to make it more interesting!

### Container Manager (gui): <a name="container"></a>
description of the feature possibly with a picture to make it more interesting!

### Job submiter: <a name="submiter"></a>
description of the feature possibly with a picture to make it more interesting!

### DB sync: <a name="db-sync"></a>
description of the feature possibly with a picture to make it more interesting!

### Locations sync: <a name="loc-sync"></a>
description of the feature possibly with a picture to make it more interesting!

### Launcher convert: <a name="launch-action"></a>
description of the feature possibly with a picture to make it more interesting!

### Event server: <a name="eserver"></a>
description of the feature possibly with a picture to make it more interesting!

### Hooks: <a name="hooks"></a>
description of the feature possibly with a picture to make it more interesting!
