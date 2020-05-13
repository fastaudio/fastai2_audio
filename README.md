![CI](https://github.com/rbracco/fastai2_audio/workflows/CI/badge.svg)

# Fastai2 Audio
> An audio module for v2 of fastai. We want to help you build audio machine learning applications while minimizing the need for audio domain expertise. Currently under development.


# Quick Start

[Google Colab Notebook](https://colab.research.google.com/gist/PranY/ba0245752fff8ec2eb645afcc13f74f6/music.ipynb)

[Zachary Mueller's class](https://youtu.be/0IQYJNkAI3k?t=1665)

## Install

In the future we will offer conda and pip installs, but as the code is rapidly changing, we recommend that only those interested in contributing and experimenting install for now. Everyone else should use [Fastai audio v1](https://github.com/mogwai/fastai_audio)

To install:

``` 
pip install packaging
pip install git+https://github.com/rbracco/fastai2_audio.git
```

If you plan on contributing to the library instead, you will need to do a editable install:

``` 
pip install packaging nbdev --upgrade
git clone https://github.com/rbracco/fastai2_audio
cd fastai2_audio
nbdev_install_git_hooks
pip install -e ".[dev]"
```

The final step sets up git hooks, which clean up the notebooks to remove the extraneous stuff stored in the notebooks (e.g. which cells you ran) which causes unnecessary merge conflicts.

Before submitting a PR, check that the local library and notebooks match. The script `nbdev_diff_nbs` can let you know if there is a difference between the local library and the notebooks.
* If you made a change to the notebooks in one of the exported cells, you can export it to the library with `nbdev_build_lib` or `make fastai2`.
* If you made a change to the library, you can export it back to the notebooks with `nbdev_update_lib`.

# Contributors
We are looking for contributors of all skill levels. If you don't have time to contribute, please at least reach out and give us some feedback on the library by posting in the [v2 audio thread](https://forums.fast.ai/t/fastai-v2-audio/53535) or contact us via PM [@baz](https://forums.fast.ai/u/baz/) or [@madeupmasters](https://forums.fast.ai/u/MadeUpMasters/)

### Active Contributors
- [kevinbird15](https://github.com/kevinbird15)
- [mogwai](https://github.com/mogwai)
- [rbracco](https://github.com/rbracco)
- [Hiromis](https://github.com/hiromis)
- [scart97](https://github.com/scart97)

### How to contribute
Create issues, write documentation, suggest/add features, submit PRs. We are open to anything. A good first step would be posting in the [v2 audio thread](https://forums.fast.ai/t/fastai-v2-audio/53535) introducing yourself 
