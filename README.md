# Maths Worksheet Generator

![sample worksheet](sample.png)

## Background
My best friend tests his 5 year old basic math questions from store-bought material which is good for one time use (his son memorizes the answers) …. but he wants to give him more practice. 

Two solutions:
1. keep buying more one time usage materials (less beer budget); or 
2. make question sets with the number pairs and calculate the answer for each question manually (less beer time)

Not ideal.

That's the reason for me to look into an automate way to get the job done.

## Benefit of the Maths Worksheet Generator
With the Maths Worksheet Generator, you can create a PDF with unique questions, as needed, in a fraction of second.

There are four choices:
1. Addition
2. Subtraction
3. Multiplication
4. Mixed

## Requirements
1. [python3](https://www.python.org/downloads/)
2. [fpdf](https://pypi.org/project/fpdf/)

## How to Use
1. Generate the worksheet in pdf format with the following command:
```
python3 run.py --type [+|-|x|mix]
```
For example, for addition only worksheet, use the following command:
```
python3 run.py --type +
```
2. Print out the generated file `worksheet.pdf`

3. You can generate more questions by editing the parameter `total_question` under `run.py`

## Sample
[sample worksheet](sample-worksheet.pdf)

## Code Overview
Everything is written in python in `run.py`. You can play with the font and grid size with the variables under the `# Basic settings` section.

## Contributing
I appreciate all suggestions or PRs which will help kids learn maths better. Feel free to create a pull request with your idea or fork the project.

## TODO
1. Add date/name/score section to the front page
2. Add support for Division
3. Pass in the range of random number with a flag (currently the default is 0-100)
4. Pass in the number of questions with a flag (currently the default is 80)

## Special Thanks
My long time friend San for the inspiration of this project and lovely sons Tim and Hin. Thanks [thedanimal](https://github.com/thedanimal) for reviewing this README.  