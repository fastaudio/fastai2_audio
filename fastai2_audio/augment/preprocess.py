# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/10_Augment_Preprocess.ipynb (unless otherwise specified).

__all__ = ['RemoveSilence', 'Resample']

# Cell
from fastai2.data.all import *
from ..core.all import *
from fastai2.vision.augment import RandTransform

# Cell
from librosa.effects import split
from scipy.signal import resample_poly

# Cell
mk_class('RemoveType', **{o:o.lower() for o in ['Trim', 'All', 'Split']},
         doc="All methods of removing silence as attributes to get tab-completion and typo-proofing")

# Cell
def _merge_splits(splits, pad):
    clip_end = splits[-1][1]
    merged = []
    i=0
    while i < len(splits):
        start = splits[i][0]
        while splits[i][1] < clip_end and splits[i][1] + pad >= splits[i+1][0] - pad:
            i += 1
        end = splits[i][1]
        merged.append(np.array([max(start-pad, 0), min(end+pad, clip_end)]))
        i+=1
    return np.stack(merged)

def RemoveSilence(remove_type=RemoveType.Trim, threshold=20, pad_ms=20):
    def _inner(ai:AudioTensor)->AudioTensor:
        '''Split signal at points of silence greater than 2*pad_ms '''
        if remove_type is None: return ai
        padding = int(pad_ms/1000*ai.sr)
        if(padding > ai.nsamples): return ai
        splits = split(ai.numpy(), top_db=threshold, hop_length=padding)
        if remove_type == "split":
            sig =  [ai[:,(max(a-padding,0)):(min(b+padding,ai.nsamples))]
                    for (a, b) in _merge_splits(splits, padding)]
        elif remove_type == "trim":
            sig = [ai[:,(max(splits[0, 0]-padding,0)):splits[-1, -1]+padding]]
        elif remove_type == "all":
            sig = [torch.cat([ai[:,(max(a-padding,0)):(min(b+padding,ai.nsamples))]
                              for (a, b) in _merge_splits(splits, padding)], dim=1)]
        else:
            raise ValueError(f"Valid options for silence removal are None, 'split', 'trim', 'all' not '{remove_type}'.")
        ai.data = torch.cat(sig, dim=-1)
        return ai
    return _inner

# Cell
def Resample(sr_new):
    def _inner(ai:AudioTensor)->AudioTensor:
        '''Resample using faster polyphase technique and avoiding FFT computation'''
        if(ai.sr == sr_new): return ai
        sig_np = ai.numpy()
        sr_gcd = math.gcd(ai.sr, sr_new)
        resampled = resample_poly(sig_np, int(sr_new/sr_gcd), int(ai.sr/sr_gcd), axis=-1)
        ai.data = torch.from_numpy(resampled.astype(np.float32))
        ai.sr = sr_new
        return ai
    return _inner