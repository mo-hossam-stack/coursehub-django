from django.template.loader import get_template
from django.conf import settings

def get_responsive_video_breakpoints():
    return {
        'mobile_small': {'width': 320, 'quality': 'auto:eco', 'bitrate': '500k'},
        'mobile_large': {'width': 640, 'quality': 'auto:eco', 'bitrate': '1m'},
        'tablet': {'width': 960, 'quality': 'auto:good', 'bitrate': '2m'},
        'desktop': {'width': 1280, 'quality': 'auto:good', 'bitrate': '4m'},
        'desktop_hd': {'width': 1920, 'quality': 'auto:best', 'bitrate': '6m'},
    }

def get_responsive_image_breakpoints():
    return [
        {'width': 320, 'dpr': 1},
        {'width': 640, 'dpr': 1},
        {'width': 960, 'dpr': 1},
        {'width': 1280, 'dpr': 1},
        {'width': 1920, 'dpr': 1},
    ]

def get_cloudinary_image_object(instance, 
                                field_name="image",
                                as_html=False,
                                width=1200,
                                format=None,
                                lazy=True,
                                responsive=False):
    if not hasattr(instance, field_name):
        return ""
    
    image_object = getattr(instance, field_name)
    if not image_object:
        return ""
    
    # Base image options with mobile optimization
    image_options = {
        "width": width,
        "crop": "fill",
        "gravity": "auto",  # Smart cropping
        "fetch_format": format or "auto",  # Auto WebP/AVIF
        "quality": "auto:best",
        "dpr": "auto",  # Device pixel ratio
    }
    
    if responsive:
        return get_responsive_image_srcset(instance, field_name, width)
    
    if as_html:
        url = image_object.build_url(**image_options)
        loading_attr = 'loading="lazy" decoding="async"' if lazy else ''
        return f'<img src="{url}" {loading_attr} alt="{getattr(instance, "title", "")}" class="w-full h-auto">'
    
    return image_object.build_url(**image_options)


def get_responsive_image_srcset(instance, field_name="image", base_width=1200):
    if not hasattr(instance, field_name):
        return {"src": "", "srcset": "", "sizes": ""}
    
    image_object = getattr(instance, field_name)
    if not image_object:
        return {"src": "", "srcset": "", "sizes": ""}
    
    breakpoints = get_responsive_image_breakpoints()
    srcset_parts = []
    
    for bp in breakpoints:
        options = {
            "width": bp['width'],
            "crop": "fill",
            "gravity": "auto",
            "fetch_format": "auto",
            "quality": "auto:best",
            "dpr": bp['dpr'],
        }
        url = image_object.build_url(**options)
        srcset_parts.append(f"{url} {bp['width']}w")
    
    default_options = {
        "width": base_width,
        "crop": "fill",
        "gravity": "auto",
        "fetch_format": "auto",
        "quality": "auto:best",
    }
    default_src = image_object.build_url(**default_options)
    
    return {
        "src": default_src,
        "srcset": ", ".join(srcset_parts),
        "sizes": "(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
    }


def get_image_placeholder(instance, field_name="image"):
    """
    Generate low-quality placeholder for blur-up effect.
    """
    if not hasattr(instance, field_name):
        return ""
    
    image_object = getattr(instance, field_name)
    if not image_object:
        return ""
    
    placeholder_options = {
        "width": 50,
        "quality": "auto:low",
        "effect": "blur:1000",
        "fetch_format": "auto",
    }
    
    return image_object.build_url(**placeholder_options)



def get_cloudinary_video_object(instance, 
                                field_name="video",
                                as_html=False,
                                width=None,
                                height=None,
                                sign_url=True,
                                fetch_format="auto",
                                quality="auto:good",
                                controls=True,
                                autoplay=False,
                                streaming_profile="hd",
                                adaptive=True):
    if not hasattr(instance, field_name):
        return ""
    
    video_object = getattr(instance, field_name)
    if not video_object:
        return ""
    
    video_options = {
        "sign_url": sign_url,
        "fetch_format": "auto",  # Smart progressive (WebM/AV1/MP4)
        "quality": "auto",       # Smart quality
        "controls": controls,
        "autoplay": autoplay,
    }
    
    # Optional: Limit width for bandwidth savings on mobile if explicitly requested
    if width is not None:
        video_options['width'] = width
        video_options['crop'] = "limit"
        
    if height is not None:
        video_options['height'] = height
        
    # NOTE: Adaptive streaming (streaming_profile) removed in favor of 
    # robust progressive download (f_auto, q_auto) for mobile stability.
    
    url = video_object.build_url(**video_options)
    
    if as_html:
        template_name = "videos/snippets/embed.html"
        tmpl = get_template(template_name)
        cloud_name = settings.CLOUDINARY_CLOUD_NAME
        
        # Get poster image
        poster_url = get_video_poster_image(instance, field_name)
        
        context = {
            'video_url': url,
            'cloud_name': cloud_name,
            'base_color': "#007cae",
            'poster_url': poster_url,
            'adaptive': adaptive,
            'quality': quality,
        }
        
        return tmpl.render(context)
    
    return url


def get_cloudinary_video_object_mobile(instance, 
                                       field_name="video",
                                       network_quality="auto"):
    quality_map = {
        'slow': 'auto:eco',
        'medium': 'auto:good',
        'fast': 'auto:best',
        'auto': 'auto:good',
    }
    
    return get_cloudinary_video_object(
        instance,
        field_name=field_name,
        as_html=True,
        quality=quality_map.get(network_quality, 'auto:good'),
        streaming_profile='hd',
        adaptive=True,
        autoplay=False,
    )


def get_video_poster_image(instance, field_name="video", time_offset=0):
    if not hasattr(instance, field_name):
        return ""
    
    video_object = getattr(instance, field_name)
    if not video_object:
        return ""
    
    poster_options = {
        "resource_type": "video",
        "format": "jpg",
        "quality": "auto:best",
        "width": 1280,
        "crop": "fill",
        "gravity": "auto",
        "start_offset": time_offset,
    }
    
    return video_object.build_url(**poster_options)


def get_video_adaptive_sources(instance, field_name="video"):
    """
    Generate multiple video sources for adaptive streaming.
    Returns list of video URLs with different quality levels.
    """
    if not hasattr(instance, field_name):
        return []
    
    video_object = getattr(instance, field_name)
    if not video_object:
        return []
    
    breakpoints = get_responsive_video_breakpoints()
    sources = []
    
    for key, config in breakpoints.items():
        options = {
            "sign_url": True,
            "fetch_format": "auto",
            "quality": config['quality'],
            "width": config['width'],
            "streaming_profile": "hd",
        }
        
        url = video_object.build_url(**options)
        sources.append({
            'url': url,
            'quality': key,
            'width': config['width'],
            'bitrate': config['bitrate'],
        })
    
    return sources