#!/usr/bin/env python
# coding=utf-8
'''
Author        : zhenghaoming
Date          : 2022-09-13 11:29:35
FilePath      : \lighttools\LightCustomPreset.py
version       : 0.1
LastEditors   : zhenghaoming
LastEditTime  : 2022-09-16 16:13:05
'''

class LightCustomPreset(object):

    TURN_ATTRI_POWER = ["on","off"]

    ATTRI_RESET_LEBAL = ["Restore All Setting","Reset All"]
    
    DEFAULT_ATTRI_LOOKUP=[
        ["Casts Shadows","castsShadows"],
        ["Receive Shadows","receiveShadows"],
        ["Hold Out","holdOut"],
        ["Motion Blur","motionBlur"],
        ["Primary Visibility","primaryVisibility"],
        ["Smooth Shading","smoothShading"],
        ["Visible In Reflections","visibleInReflections"],
        ["Visible In Refractions","visibleInRefractions"],
        ["Double Sided","doubleSided"],
        ["Opposite","opposite"],

    ]

    DEFAULT_ATTRI_VALUE = [1,1,0,1,1,1,1,1,1,1]

    ARNOLD_ATTRI_LOOKUP=[
        ["Opaque","aiOpaque"],
        ["Matte","aiMatte"],
        ["Primary Visibility","primaryVisibility"],
        ["Casts Shadows","castsShadows"],
        ["Diffuse Reflection","aiVisibleInDiffuseReflection"],
        ["Specular Reflection","aiVisibleInSpecularReflection"],
        ["Diffuse Transmission","aiVisibleInDiffuseTransmission"],
        ["Specular Transmission","aiVisibleInSpecularTransmission"],
        ["Volume","aiVisibleInVolume"],
        ["Self Shadows","aiSelfShadows"],

    ]

    ARNOLD_ATTRI_DEFAULT_VALUE = [1,0,1,1,1,1,1,1,1,1]
    # ARNOLD_SUBDIVISION = 

    REDSHIFT_ATTRI_LOOKUP=[
        ["Redshift Visibility Overrides","rsEnableVisibilityOverrides"],
        ["Primary Ray Visible","rsPrimaryRayVisible"],
        ["Secondary Ray Visible","rsSecondaryRayVisible"],
        ["Casts Shadow","rsShadowCaster"],
        ["Receives Shadow","rsShadowReceiver"],
        ["Self-Shadows","rsSelfShadows"],
        ["Caster AO","rsAOCaster"],
        ["Reflection In Visible","rsReflectionVisible"],
        ["Refraction In Visible","rsRefractionVisible"],
        ["Casts Reflection","rsReflectionCaster"],
        ["Casts Refraction","rsRefractionCaster"],
        ["Visible to Non-Photon GI","rsFgVisible"],
        ["Visible to GI Photons","rsGiVisible"],
        ["Visible to Caustic Photons","rsCausticVisible"],
        ["Receives GI","rsFgCaster"],
        ["Force Brute-Force GI","rsForceBruteForceGI"],
        ["Casts GI Photons","rsGiCaster"],
        ["Casts Caustic Photons","rsCausticCaster"],
        ["Receives GI Photons","rsGiReceiver"],
        ["Receives Caustic Photons","rsCausticReceiver"],

    ]

    REDSHIFT_ATTRI_DEFAULT_VALUE = [0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,0,1,0,1,1]

    DEFAULT_LIGHT_TYPE={
        "spot":["spotlight.png",],
        "dir":["directionallight.png",],
        "point":["pointlight.png",],
        "amb":["ambientlight.png",],
        "area":["arealight.png",],
    }
    
    ARNOLD_LIGHT_TYPE={
        'area':["AreaLightShelf.png","aiAreaLight"],
        'mesh':["MeshLightShelf.png","aiMeshLight"],
        'photo':["PhotometricLightShelf.png","aiPhotometricLight"],
        'skydome':["SkydomeLightShelf.png","aiSkyDomeLight"],
        'port':["LightPortalShelf.png","aiLightPortal"],
        'physicalsky':["PhysicalSkyShelf.png","aiSkyDomeLight"],
    }

    REDSHIFT_LIGHT_TYPE={
        'dir': ['rs_lightDirectional.svg','directionalLight','RedshiftPhysicalLight'],
        'area': ['rs_lightArea.svg','areaLight','RedshiftPhysicalLight'],
        'point': ['rs_lightPoint.svg','pointLight','RedshiftPhysicalLight'],
        'spot': ['rs_lightSpot.svg','spotLight','RedshiftPhysicalLight'],
        'port': ['rs_lightPortal.svg','PortalLight','RedshiftPortalLight'],
        'ies': ['rs_lightIES.svg','IESLight','RedshiftIESLight'],
        'sun': ['rs_lightSunSky.svg','PhysicalSun','RedshiftPhysicalSun'],
        'skydome': ['rs_lightDome.svg','DomeLight','RedshiftDomeLight'],
    }

    LGT_TYPES_DEFAULT = [
        "ambientLight",
        "pointLight",
        "spotLight",
        "areaLight",
        "directionalLight",
        "volumeLight"
    ]

    LGT_TYPES_ARNOLD = [
        "aiAreaLight",
        "aiMeshLight",
        "aiLightPortal",
        "aiPhotometricLight",
        "aiSkyDomeLight"
    ]

    LGT_TYPES_REDSHIFT = [
        "RedshiftPhysicalLight",
        "RedshiftPortalLight",
        "RedshiftIESLight",
        "RedshiftPhysicalSun",
        "RedshiftDomeLight"
    ]

    LGT_ATTRS_DEFAULT = [
        "coneAngle",
        "penumbraAngle",
        "transmission",
        "dropoff",
        "decayRate",
        "emitDiffuse",
        "emitSpecular",
        "intensity",
        "shadowColor",
        "fogSpread",
        "fogIntensity",
        "camera",
        "format",
        "portalMode",
        "color" ]

    LGT_ATTRS_ARNOLD = [
        "aiExposure",
        "aiSamples",
        "aiUseColorTemperature",
        "aiColorTemperature",
        "aiRadius",
        "aiAngle",
        "aiSpread",
        "aiDiffuse",
        "aiSpecular",
        "aiSss",
        "aiIndirect",
        "aiVolume",
        "aiMaxBounces",
        "aiNormalize",
        "aiRoundness",
        "aiCastShadows",
        "aiShadowDensity",
        "aiAspectRatio",
        "aiLensRadius",
        "aiVolumeSamples",
        "aiCastVolumetricShadows",
        "aiNormalize",
        "aiShadowColor",
        "aiShadowDensity" ]

    LGT_ATTRS_REDSHIFT = [
        "lightType",
        "colorMode",
        "temperature",
        "unitsType",
        "lumensperwatt",
        "exposure",
        "affectsDiffuse",
        "affectsSpecular",
        "decayType",
        "falloffStart",
        "falloffStop",
        "lightType",
        "areaShape",
        "areaVisibleInRender",
        "areaBidirectional",
        "areaSamples",
        "spotConeAngle",
        "spotConeFalloffAngle",
        "spotConeFalloffCurve",
        "shadowTransparency",
        "SAMPLINGOVERRIDES_shadowSamplesScale",
        "SAMPLINGOVERRIDES_numShadowSamples",
        "shadow",
        "volumeRayContributionScale",
        "volumeNumSamples"
        ]