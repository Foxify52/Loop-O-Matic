# Loop-O-Matic
This awful piece of software is the loop-o-matic. It's a simple program that allows you to create a meh quality extention of any given song. This was my sad attempt at making a stripped down clone of the incredible [Eternal Jukebox](https://jukebox.davi.gq/jukebox_index.html) that didn't rely on spotify or youtube.

## Usage
Run `poetry install --no-root`.

Run `main.py`. Make sure you fill out the settings. They have comments telling you what goes where.

## Known Issues
The jumps are not perfect. They are a little bit off.
It also has issues with the beats being played twice. This is because the beat detection within librosa is a little bit off which throws the whole algorithm off.
Nothing I know what to do about either one of these issues so if you do, feel free to leave a PR.

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