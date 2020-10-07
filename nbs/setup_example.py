from fastai.data.all import *
from fastai2_audio.core.all import *
from fastai.vision.augment import RandTransform

__all__ = ["ex_files", "GenExample", "show_transform"]

p = untar_data(URLs.SPEAKERS10, extract_func=tar_extract_at_filename)
files = get_audio_files(p)

#files will load differently on different machines so we specify examples by name
ex_files = [p/f for f in ['m0005_us_m0005_00218.wav', 
                                'f0003_us_f0003_00279.wav', 
                                'f0001_us_f0001_00168.wav', 
                                'f0005_us_f0005_00286.wav',]]

#sc= single channel, mc = multichannel
@docs
class GenExample:
    "Generate individual or batch of single/multichannel AudioTensors and AudioSpectrograms for testing"
    
    
    def audio_sc(): return AudioTensor.create(ex_files[0])

    def audio_mc():
        #get 3 equal length portions of 3 different signals so we can stack them
        #for a fake multichannel example
        ai0, ai1, ai2 = map(AudioTensor.create, ex_files[1:4]);
        min_samples = min(ai0.nsamples, ai1.nsamples, ai2.nsamples)
        s0, s1, s2 = map(lambda x: x[:,:min_samples], (ai0, ai1, ai2))
        return AudioTensor(torch.cat((s0, s1, s2), dim=0), 16000)

    def audio_sc_batch(bs=8):
        return AudioTensor(torch.stack([AudioTensor.create(ex_files[0]) for i in range(bs)]), 16000)

    def audio_mc_batch(bs=8):
        return AudioTensor(torch.stack([GenExample.audio_mc() for i in range(bs)]), 16000)
    
    def sg_sc():
        DBMelSpec = SpectrogramTransformer(mel=True, to_db=True)
        a2s = DBMelSpec(n_fft = 1024, hop_length=256)
        return a2s(GenExample.audio_sc())
    def sg_mc(): 
        DBMelSpec = SpectrogramTransformer(mel=True, to_db=True)
        a2s = DBMelSpec(n_fft = 1024, hop_length=256)
        return a2s(GenExample.audio_mc())
    
    _docs=dict(audio_sc="Generate a single-channel audio", 
               audio_mc="Generate a multi-channel audio", 
               audio_sc_batch="Generate a batch of single-channel audios", 
               audio_mc_batch="Generate a batch of multi-channel audios",
               sg_sc="Generate a spectrogram of a single-channel audio",
               sg_mc="Generate a spectrogram of a multi-channel audio",
               #sg_sc_batch="Generate a batch of spectrograms of a single-channel audios",
              )
    
# Warning: calling inp.clone() does not copy it's attributes,
# such as sr in the case of an AudioTensor. 
# Since transforms mutate in place, any testing that requires
# the input sample rate must store the sample rate before the
# transform so that it may be tested after.
# See the tests in resampling for an example

def maybe_show(item, show, hear):
    if show: item.show(hear=hear)
    elif hear: item.hear()

def show_transform(transform, gen_input=GenExample.audio_sc, show=True, hear=False):
    '''Generate a new input, apply transform, and display/return both input and output'''
    inp = gen_input()
    inp_orig = inp.clone()
    maybe_show(inp, show, hear)
    out = transform(inp, split_idx=0) if isinstance(transform, RandTransform) else transform(inp)
    maybe_show(out, show, hear)
    return inp_orig, out

if __name__ == '__main__':
    aud_ex = GenExample.audio_sc()
    aud_mc_ex = GenExample.audio_mc()
    aud_batch = GenExample.audio_sc_batch(4)
    aud_mc_batch = GenExample.audio_mc_batch(8)
    test_eq(type(aud_ex), AudioTensor)
    test_eq(type(aud_batch), AudioTensor)
    test_eq(aud_batch.shape, torch.Size([4, 1, 58240]))
    test_eq(aud_mc_batch.shape, torch.Size([8, 3, 53760]))
