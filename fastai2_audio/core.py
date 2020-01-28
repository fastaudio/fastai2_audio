# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/00_core.ipynb (unless otherwise specified).

__all__ = ['audio_extensions', 'get_audio_files', 'AudioGetter', 'AudioTensor', 'show_audio_signal', 'OpenAudio',
           'AudioSpectrogram', 'show_spectrogram', 'AudioToSpec', 'fill_pipeline', 'SpectrogramTransformer',
           'warn_unused', 'get_usable_kwargs', 'AudioToMFCC', 'config_from_func', 'AudioConfig']

# Cell
from fastai2.torch_basics import *
from fastai2.data.all import *
import torchaudio
import torchaudio.transforms as torchaud_tfm
import warnings

from IPython.display import display, Audio
from dataclasses import dataclass, asdict, is_dataclass, make_dataclass
from torchaudio.transforms import Spectrogram, AmplitudeToDB, MFCC
from librosa.display import specshow, waveplot
from inspect import signature
from functools import partial

# Cell
audio_extensions = tuple(str.lower(k) for k, v in mimetypes.types_map.items() if v.startswith('audio/'))

# Cell
def get_audio_files(path, recurse=True, folders=None):
    "Get image files in `path` recursively, only in `folders`, if specified."
    return get_files(path, extensions=audio_extensions, recurse=recurse, folders=folders)

# Cell
def AudioGetter(suf='', recurse=True, folders=None):
    "Create `get_image_files` partial function that searches path suffix `suf` and passes along `kwargs`, only in `folders`, if specified."
    def _inner(o, recurse=recurse, folders=folders):
        return get_audio_files(o/suf, recurse, folders)
    return _inner

# Cell
URLs.SPEAKERS10 = 'http://www.openslr.org/resources/45/ST-AEDS-20180100_1-OS'
URLs.SPEAKERS250 = 'https://public-datasets.fra1.digitaloceanspaces.com/250-speakers.tar'
URLs.ESC50 = 'https://github.com/karoldvl/ESC-50/archive/master.zip'

# Cell
class AudioTensor(TensorBase):
    @classmethod
    @delegates(torchaudio.load, keep=True)
    def create(cls, fn, **kwargs):
        sig, sr = torchaudio.load(fn, **kwargs)
        return cls(sig, sr=sr)

    @property
    def sr(self): return self.get_meta('sr')

    def __new__(cls, x, sr, **kwargs):
        return super().__new__(cls, x, sr=sr, **kwargs)

    # This one should probably use set_meta() but there is no documentation,
    # and I could not get it to work. Even TensorBase.set_meta?? is pointing
    # to the wrong source because of fastai patch on Tensorbase to retain types
    @sr.setter
    def sr(self, val): self._meta['sr'] = val

    nsamples, nchannels = add_props(lambda i, self: self.shape[-1*(i+1)])
    @property
    def duration(self): return self.nsamples/float(self.sr)

    def hear(self):
        display(Audio(self, rate=self.sr))
    def show(self, ctx=None, **kwargs):
        "Show image using `merge(self._show_args, kwargs)`"
        self.hear()
        show_audio_signal(self, ctx=ctx, **kwargs)
        plt.show()

# Cell
def _get_f(fn):
    def _f(self, *args, **kwargs):
        cls = self.__class__
        res = getattr(super(TensorBase, self), fn)(*args, **kwargs)
        return retain_type(res, self)
    return _f
setattr(AudioTensor, '__getitem__', _get_f('__getitem__'))

# Cell
def show_audio_signal(ai, ctx, **kwargs):
    if(ai.nchannels > 1):
        _,axs = plt.subplots(ai.nchannels, 1, figsize=(6,4*ai.nchannels))
        for i,channel in enumerate(ai):
            waveplot(channel.numpy(), ai.sr, ax=axs[i], **kwargs)
    else:
        axs = plt.subplots(ai.nchannels, 1)[1] if ctx is None else ctx
        waveplot(ai.squeeze(0).numpy(), ai.sr, ax=axs, **kwargs)

# Cell
class OpenAudio(Transform):
    def __init__(self, items):
        self.items = items

    def encodes(self, i):
        o = self.items[i]
        return AudioTensor.create(o)

    def decodes(self, i)->Path:
        return self.items[i]

# Cell
_GenSpec    = torchaudio.transforms.Spectrogram
_GenMelSpec = torchaudio.transforms.MelSpectrogram
_GenMFCC    = torchaudio.transforms.MFCC
_ToDB       = torchaudio.transforms.AmplitudeToDB

# Cell
class AudioSpectrogram(TensorImageBase):
    @classmethod
    def create(cls, sg_tensor, settings=None):
        audio_sg = cls(sg_tensor)
        audio_sg._settings = settings
        return audio_sg

    @property
    def duration(self):
        # spectrograms round up length to fill incomplete columns,
        # so we subtract 0.5 to compensate, wont be exact
        return (self.hop_length*(self.shape[-1]-0.5))/self.sr

    height, width = add_props(lambda i, self: self.shape[i+1], n=2)
    #using the line below instead of above will fix show_batch but break multichannel/delta display
    #nchannels, height, width = add_props(lambda i, self: self.shape[i], n=3)

    def __getattr__(self, name):
        if name == "settings": return self._settings
        if not name.startswith('_'): return self._settings[name]
        raise AttributeError(f"{self.__class__.__name__} object has no attribute {name}")

    def show(self, ctx=None, ax=None, figsize=None, **kwargs):
        show_spectrogram(self, ctx=ctx, ax=ax, figsize=figsize,**kwargs)
        plt.show()

# Cell
def show_spectrogram(sg, ax, ctx, figsize, **kwargs):
    ax = ifnone(ax,ctx)
    nchannels = sg.nchannels
    r, c = nchannels, sg.data.shape[0]//nchannels
    proper_kwargs = get_usable_kwargs(specshow, sg._settings, exclude=["ax", "kwargs", "data",])
    if (r == 1 and c == 1):
        _show_spectrogram(sg, ax, proper_kwargs, **kwargs)
        plt.title("Channel 0 Image 0: {} X {}px".format(*sg.shape[-2:]))
    else:
        if figsize is None: figsize = (4*c, 3*r)
        if ax is None: _,ax = plt.subplots(r, c, figsize=figsize)
        for i, channel in enumerate(sg.data):
            if r == 1:
                cur_ax = ax[i%c]
            elif c == 1:
                cur_ax = ax[i%r]
            else:
                cur_ax = ax[i//c,i%c]
            width,height = sg.shape[-2:]
            cur_ax.set_title(f"Channel {i//c} Image {i%c}: {width} X {height}px")
            z = specshow(channel.numpy(), ax=cur_ax, **sg._show_args, **proper_kwargs)
            #plt.colorbar(z, ax=cur_ax)
            #ax=plt.gca() #get the current axes
            #PCM=ax.get_children()[2] #get the mappable, the 1st and the 2nd are the x and y axes
            #plt.colorbar(PCM, ax=ax, format='%+2.0f dB')

def _show_spectrogram(sg, ax, proper_kwargs, **kwargs):
    if "mel" not in sg._settings: y_axis = None
    else:                        y_axis = "mel" if sg.mel else "linear"
    proper_kwargs.update({"x_axis":"time", "y_axis":y_axis,})
    _ = specshow(sg.data.squeeze(0).numpy(), **sg._show_args, **proper_kwargs)
    fmt = '%+2.0f dB' if "to_db" in sg._settings and sg.to_db else '%+2.0f'
    plt.colorbar(format=fmt)

# Cell
class AudioToSpec(Transform):
    def __init__(self, pipe, settings):
        self.pipe = pipe
        self.settings = settings

    @classmethod
    def from_cfg(cls, audio_cfg):
        cfg = asdict(audio_cfg) if is_dataclass(audio_cfg) else dict(audio_cfg)
        transformer = SpectrogramTransformer(mel=cfg.pop("mel"), to_db=cfg.pop("to_db"))
        return transformer(**cfg)

    def encodes(self, audio:AudioTensor):
        self.settings.update({'sr':audio.sr, 'nchannels':audio.nchannels})
        return AudioSpectrogram.create(self.pipe(audio.data), settings=dict(self.settings))

# Cell
def fill_pipeline(transform_list, sg_type, **kwargs):
    '''Adds correct args to each transform'''
    kwargs = _override_bad_defaults(dict(kwargs))
    function_list = L()
    settings = {}
    for f in transform_list:
        usable_kwargs = get_usable_kwargs(f, kwargs)
        function_list += f(**usable_kwargs)
        settings.update(usable_kwargs)
    warn_unused(kwargs, settings)
    return AudioToSpec(Pipeline(function_list), settings={**sg_type, **settings})

def SpectrogramTransformer(mel=True, to_db=True):
    sg_type = dict(locals())
    transforms = _get_transform_list(sg_type)
    pipe_noargs = partial(fill_pipeline, sg_type=sg_type, transform_list=transforms)
    pipe_noargs.__signature__ = _get_signature(transforms)
    return pipe_noargs

def _get_signature(transforms):
    '''Looks at transform list and extracts all valid args for tab completion'''
    delegations = [delegates(to=f, keep=True) for f in transforms]
    out = lambda **kwargs: None
    for d in delegations: out = d(out)
    return signature(out)

def _get_transform_list(sg_type):
    '''Builds a list of higher-order transforms with no arguments'''
    transforms = L()
    if sg_type["mel"]:   transforms += _GenMelSpec
    else:                transforms += _GenSpec
    if sg_type["to_db"]: transforms += _ToDB
    return transforms

def _override_bad_defaults(kwargs):
    if "n_fft" not in kwargs or kwargs["n_fft"] is None:            kwargs["n_fft"] = 1024
    if "win_length" not in kwargs or kwargs["win_length"] is None:  kwargs["win_length"] = kwargs["n_fft"]
    if "hop_length" not in kwargs or kwargs["hop_length"] is None:  kwargs["hop_length"] = int(kwargs["win_length"]/2)
    return kwargs

def warn_unused(all_kwargs, used_kwargs):
    unused_kwargs = set(all_kwargs.keys()) - set(used_kwargs.keys())
    for kwarg in unused_kwargs:
        warnings.warn(f"{kwarg} is not a valid arg name and was not used")

# Cell
def get_usable_kwargs(func, kwargs, exclude=None):
    exclude = ifnone(exclude, [])
    defaults = {k:v.default for k, v in inspect.signature(func).parameters.items() if k not in exclude}
    usable = {k:v for k,v in kwargs.items() if k in defaults}
    return {**defaults, **usable}

# Cell
@delegates(_GenMFCC.__init__)
class AudioToMFCC(Transform):
    def __init__(self,**kwargs):
        func_args = get_usable_kwargs(_GenMFCC, kwargs, [])
        self.transformer = _GenMFCC(**func_args)
        self.settings = func_args

    @classmethod
    def from_cfg(cls, audio_cfg):
        cfg = asdict(audio_cfg) if is_dataclass(audio_cfg) else audio_cfg
        return cls(**cfg)

    def encodes(self, x:AudioTensor):
        sg_settings = {"sr":x.sr, 'nchannels':x.nchannels, **self.settings}
        return AudioSpectrogram.create(self.transformer(x).detach(), settings=sg_settings)

# Cell
def config_from_func(func, name, **kwargs):
    params = inspect.signature(func).parameters.items()
    namespace = {k:v.default for k, v in params}
    namespace.update(kwargs)
    return make_dataclass(name, namespace.keys(), namespace=namespace)

# Cell
class AudioConfig():
    #default configurations from the wrapped function
    #make sure to pass in mel=False as kwarg for non-mel spec, and to_db=False for non db spec
    BasicSpectrogram    = config_from_func(_GenSpec, "BasicSpectrogram", mel=False, to_db=True)
    BasicMelSpectrogram = config_from_func(_GenMelSpec, "BasicMelSpectrogram", mel=True, to_db=True)
    BasicMFCC           = config_from_func(_GenMFCC, "BasicMFCC ")
    #special configs with domain-specific defaults

    Voice = config_from_func(_GenMelSpec, "Voice", mel="True", to_db="False", f_min=50., f_max=8000., n_fft=1024, n_mels=128, hop_length=128)