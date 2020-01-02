import argparse

parser = argparse.ArgumentParser()

parser.add_argument('--test')
opt, _ = parser.parse_known_args()
print(opt.test)
parser.set_defaults(test=3)



opt, _ = parser.parse_known_args()
print(opt.test)

opt.test =2
opt, _ = parser.parse_known_args()

print(opt.test)
