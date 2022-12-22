# Toy HPO ontology

Prepare HPO module that consists of selected terms from different organ systems.

The module contains following terms and their ancestors:
- Arachnodactyly HP:0001166
- Focal clonic seizure HP:0002266
- Perimembranous ventricular septal defect HP:0011682
- Hepatosplenomegaly HP:0001433
- Tubularization of Bowman capsule HP:0032648
- Intercostal muscle weakness HP:0004878
- Enuresis nocturna HP:0010677
- Spasticity HP:0001257
- Chronic pancreatitis HP:0006280


Prepare the toy JSON by running the following [robot](https://robot.obolibrary.org) commands:

```shell
HPO=https://github.com/obophenotype/human-phenotype-ontology/releases/download/v2022-10-05/hp.obo
module load robot/1.8.3

wget $HPO

# Arachnodactyly HP:0001166
robot extract --input hp.obo --method BOT --term HP:0001166 \
  convert --output arachnodactyly.hp.obo

# Focal clonic seizure HP:0002266
robot extract --input hp.obo --method BOT --term HP:0002266 \
  convert --output fcs.hp.obo

# Perimembranous ventricular septal defect HP:0011682
robot extract --input hp.obo --method BOT --term HP:0011682 \
  convert --output pvsd.hp.obo

# Hepatosplenomegaly HP:0001433
robot extract --input hp.obo --method BOT --term HP:0001433 \
  convert --output hepatosplenomegaly.hp.obo

# Tubularization of Bowman capsule HP:0032648
robot extract --input hp.obo --method BOT --term HP:0032648 \
  convert --output bowman.hp.obo

# Intercostal muscle weakness HP:0004878
robot extract --input hp.obo --method BOT --term HP:0004878 \
  convert --output intercostal.hp.obo

# Enuresis nocturna HP:0010677
robot extract --input hp.obo --method BOT --term HP:0010677 \
  convert --output enuresis.hp.obo

# Spasticity HP:0001257
robot extract --input hp.obo --method BOT --term HP:0001257 \
  convert --output spasticity.hp.obo

# Chronic pancreatitis HP:0006280
robot extract --input hp.obo --method BOT --term HP:0006280 \
  convert --output cp.hp.obo


# Merge into one file
robot merge --input arachnodactyly.hp.obo \
  --input fcs.hp.obo \
  --input pvsd.hp.obo \
  --input hepatosplenomegaly.hp.obo \
  --input bowman.hp.obo \
  --input intercostal.hp.obo \
  --input enuresis.hp.obo \
  --input spasticity.hp.obo \
  --input cp.hp.obo \
  --output hp.toy.json

rm *.obo
```
