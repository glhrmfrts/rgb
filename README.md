# rgb
A pygame platformer game where your color matters!

The rule is: You don't collide with anything that has the same color with you. So you must find your way through the obstacles by changing your color.

Take a look: (Please note I'm not a game designer c:)

![Screenshot](https://raw.githubusercontent.com/glhrmfrts/rgb/master/assets/rgb.png)

Visit **Controls** menu in the game for more information.

## Playing
First install all the requirements:

`pip install -r requirements.txt`

Then if you want to run directly from Python:

`python ./src/main.py`

Or to build the executable:

`python ./setup.py build`

This will generate a `./build/__your_platform__` directory, where **\_\_your_platform\_\_** is your machine architecture. Then cd into that directory and run `./rgb`, if you have any problems, copy the **assets** folder into that directory.

## Arguments
To run with the FPS displaying on the screen: (`rgb` here is the executable or the main.py script, it doesn't matter)

`rgb -d`

To start from a given level:

`rgb -l [level_number]`

Then go to the **Play -> New Game** menu.

You can use all arguments together.

## Levels
The game currently has 11 levels, built with [Tiled](http://www.mapeditor.org/) and saved as a json file. The `Map` class at `src/map.py` is responsible for loading the level map.

Every object in a level is loaded dynamically from the json file. If you haven't, I recommend you to download Tiled then you can take a look at how the maps are created.


## Bugs
The game is not complete, so there are bugs. The most notable one is the physics in level 9 where you are supposed to repeatedly gain impulse from the **ImpulseBlock** but it is not working right now :p. ~~I plan to switch to a physics engine in the near future, but if you have any ideas and/or want to contribute, just send a pull request.~~ I plan to re-build this game from scratch using other programming language and OpenGL.
