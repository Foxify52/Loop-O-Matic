# Loop-O-Matic
This piece of software is the loop-o-matic. It's a simple program that allows you to create a somewhat decent quality extention of any given song. This was my attempt at making a stripped down clone of the incredible [Eternal Jukebox](https://jukebox.davi.gq/jukebox_index.html) that didn't rely on spotify or youtube. The quality of the algorithm has since been improved, but it's still not perfect.

## Usage
Run `poetry install --no-root`.

Run `main.py`. Make sure you fill out the settings. They have comments telling you what goes where.

## Known Issues
The jumps are sometimes happening between two segments that are not similar. I'm not sure why this is happening despite the precision of the jump detection.
It doesn't play nice with some songs. I'm not sure why. I think it has something to do with librosa.

## Licensing
   Copyright 2023 Foxify52

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.