# Training Method

## usage:
`python train.py`

## requirements:

## details:

The following is programmed in `train.py`:  
Under `if __name__ == '__main__':`, the first three lines parse the training options `opt`;creates the `game` according to `opt`, (which specifies which game and further details); creates the `model` according to `opt` and `game` (which specifies which model, game input/action size and other parameters).
Then it creates the `montetree` with `opt`, `game`, and `model` and coacher with `opt`, `game`, `model` and `montetree`. `coacher.learn()` performs the training actions.

