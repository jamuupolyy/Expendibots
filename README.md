# Expendibots game playing agent

This was projects 1 and 2 from Semester 1 2020 Artificial Intelligence (COMP30024).

The goal was to build a game playing agent that would utilise adversarial algorithmic strategies to beat opponents.
The first project was to implement an agent that would use efficient search algorithms in order to traverse the games space, while the second expanded this into a full game playing agent.

Our agent was built utilising the negamax algorithm which assumes zero-sum properties about evaluating possible moves, along with specific heuristics in order to reduce our game playing search space.

---
Running the game:

To play a game, navigate to `partB` ensuring that the referee package (the directory `referee`) and the player package (`albanianRodentDinner`) are both within your current directory. Then run the following command:

`python -m referee <white package> <black package>` 

where python is the name of a Python 3.6 interpreter and `<white package>` `<black package>` are the names of packages containing the class Player to be used for White and Black, respectively. 

For our project, we simply pitted our agent against itself, using `<white package> = albanianRodentDinner` and `<black package> = albanianRodentDinner2`.
