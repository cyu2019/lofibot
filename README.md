# lofibot

hey boys

This is a small webapp written in node.js and python for MLH Local Hack Day. It will accept a 2 or 4 measure 4/4 sample and generate a short lofi hip hop song from it.

It can either be run from the command line or from a gui.
Installation Commands:
```
pip install pydub
pip install librosa
npm install
```
You will also need to install ffmpeg and add it to your path.

Run
```
node web
```
Then access localhost:8080 in your web browser.

To use from the command line, use:
```
python script.py filename bpm number_of_measures
```
There are some example samples in the form loop_bpm_numMeasures.wav in the repository as well.

Happy Lofing!


