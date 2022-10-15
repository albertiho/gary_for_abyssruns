# gary_for_abyssruns
gary who performs abyss runs

this is the second gary in the gary series. manually doing the runs is easily 2x faster but this guy can do it while ur sleeping

## Installing
This was developed using `Python3.9` and it is recommended to use the same version to run it.

The program should run like any other python program (by typing `python gary.py` to your terminal while in the project folder)

After you've tested that you can launch the program, open the `gary.py`-file in a text editor (e.g. notepad) and change the values of variables which start with `KEYBIND_` to match yours. This way the gary will perform correct inputs in correct places.

`KEYBIND_FOR_FIRST_PRESET` should be your main preset which has the pouches and p ess. `SECOND_PRESET` is used to refresh your familiar after the first one runs out.

You should also update the `DEFAULT_MAX_RUN_TIME` to a smaller one if you will run out of p ess. Gary doesnt care if you have p ess or not and will continue running until the `DEFAULT_MAX_RUN_TIME` has passed or you stop the program.

If you arent using extreme rc pots, just define some keybind for it thats going to be pressed every 6min when banking

If you arent using powerbursts why are you trying to rc

## Setting up in-game
You'll need to have your main action bar slots 1-8 set up exactly like this one. Your keybinds shouldnt matter but having a lot of text in the 1-8 slots might cause the program to fail to confirm that your main action bar is actually set up correctly. Remember to turn off action-bar binding so that your action bar doesnt change when banking.

![image](https://user-images.githubusercontent.com/47183301/195995383-73a46c17-9b1a-4815-91c4-e6efc9690b36.png)

The order of pouches from left to right is: Massive, Giant, Medium, Large, Small. They are not in size order for more efficient inventory space usage.

Here are the in-game settings used in development and testing:

![image](https://user-images.githubusercontent.com/47183301/195995612-08a8abf4-a952-4aad-b789-dbf604e4d756.png)

![image](https://user-images.githubusercontent.com/47183301/195995524-46e2db97-a4d7-45ba-89c3-9e37c4151bde.png)

![image](https://user-images.githubusercontent.com/47183301/195995541-e81272cd-d180-4240-bcd3-899343c164bd.png)

If the gary is having trouble locating something, changing your settings to these might help.

gary expects you to use correct relics for this activity

![image](https://user-images.githubusercontent.com/47183301/195995935-1c399950-ea3d-4a8c-9b49-23974436367b.png)

nexus mod is needed for gary to work.

![image](https://user-images.githubusercontent.com/47183301/195996537-a5e5edcd-b796-4e49-b3c3-dc7d56dbb633.png)

The wildy slay master must be visible on your minimap if standing in edgeville bank for gary to work.

Gary has been developed and tested while using 1800x1700 sized square client. Running gary when not full screened is advisable so gary has less space to search.

## Launching gary

To have gary succesfully launch, go to any bank in-game, summon your familiar and pull out your preset you wish to use. Turn gary on with your bank open, this is needed to locate the lock-icon on top of inventory to tell gary when bank is open. Gary will then teleport and start running. 

Gary will try to tell you if something is messed up in your setup (e.g. cant find main actionbar) but its not perfect.

## Final words

The code is free to use but please dont scale it up to a big farm, lets just enjoy some 


