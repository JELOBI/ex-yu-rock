# Usage: python3 optimize_pdf.py in.pdf out.pdf 65 0.6   (JPEG quality, image scale). Needs: pip install pikepdf pillow
import sys, io, zlib, pikepdf
from pikepdf import Pdf, Name
from PIL import Image, ImageCms, ImageChops
src, dst, q, scale = sys.argv[1], sys.argv[2], int(sys.argv[3]), float(sys.argv[4])
srgb = ImageCms.createProfile('sRGB')
def load(obj):
    f = obj.get('/Filter')
    fl = [str(x) for x in (f if isinstance(f, pikepdf.Array) else [f])]
    if fl == ['/DCTDecode']:
        im = Image.open(io.BytesIO(obj.read_raw_bytes())); im.load()
        cs = obj.get('/ColorSpace')
        if isinstance(cs, pikepdf.Array) and str(cs[0]) == '/ICCBased' and not im.info.get('icc_profile'):
            im.info['icc_profile'] = cs[1].read_bytes()
        return im
    raw = obj.read_bytes()
    mode = 'L' if str(obj.ColorSpace) == '/DeviceGray' else 'RGB'
    return Image.frombytes(mode, (int(obj.Width), int(obj.Height)), raw)
pdf = Pdf.open(src)
done = set()
for page in pdf.pages:
    xo = page.Resources.get('/XObject', {})
    for k, obj in list(xo.items()):
        if obj.get('/Subtype') != '/Image' or obj.objgen in done: continue
        done.add(obj.objgen)
        w, h = int(obj.Width), int(obj.Height)
        if w < 1000:  # small logos/photos: leave untouched
            if '/SMask' in obj: done.add(obj.SMask.objgen)
            continue
        nw, nh = int(w*scale), int(h*scale)
        if '/SMask' in obj:
            sm = obj.SMask; done.add(sm.objgen)
            sim = load(sm).convert('L').resize((nw, nh), Image.LANCZOS)
            sm.write(zlib.compress(sim.tobytes(), 9), filter=Name.FlateDecode)
            sm.Width, sm.Height = nw, nh
            for key in ('/DecodeParms','/Decode'):
                if key in sm: del sm[key]
        im = load(obj)
        if im.mode == 'CMYK':
            if 'adobe' in im.info: im = ImageChops.invert(im)
            icc = im.info.get('icc_profile')
            if icc:
                im = ImageCms.profileToProfile(im, ImageCms.ImageCmsProfile(io.BytesIO(icc)), srgb, outputMode='RGB')
            else: im = im.convert('RGB')
        else: im = im.convert('RGB')
        im = im.resize((nw, nh), Image.LANCZOS)
        buf = io.BytesIO(); im.save(buf, 'JPEG', quality=q, optimize=True, subsampling=2)
        obj.write(buf.getvalue(), filter=Name.DCTDecode)
        obj.Width, obj.Height = nw, nh
        obj.ColorSpace = Name.DeviceRGB; obj.BitsPerComponent = 8
        for key in ('/DecodeParms','/Decode'):
            if key in obj: del obj[key]
pdf.remove_unreferenced_resources()
pdf.save(dst, compress_streams=True, object_stream_mode=pikepdf.ObjectStreamMode.generate)
