The tool by default produces an output file called:
`IQA_predictions_<timestamp>.csv` so it depends on the current time. There is
a `-f` input (CLI) parameter that allows the user to specify the output file name.

In the [metadata CWL file](../../metadata/iqa_dce.cwl) we have added a default
value for the `-f` parameter and made it hidden to the user so the output should
alwasy be `IQA_predictions.csv`.
