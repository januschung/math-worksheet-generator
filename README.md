# Math Worksheet Generator

![sample worksheet](sample.png)
![sample answer sheet](sample-answer.png)

## Background
My best friend tests his 5 year old basic math questions from store-bought material which is good for one time use (his son memorizes the answers) …. but he wants to give him more practice.

Two solutions:
1. keep buying more one time usage materials (less beer budget); or
2. make question sets with the number pairs and calculate the answer for each question manually (less beer time)

Not ideal.

That's the reason for me to look into an automate way to get the job done.

## Benefit of the Math Worksheet Generator
With the Maths Worksheet Generator, you can create a PDF with unique questions, as needed, in a fraction of second.

There are five choices:
1. Addition
2. Subtraction
3. Multiplication
4. Division
5. Mixed

## Requirements
[python3](https://www.python.org/downloads/)

Install required package with the following command:
```
pip install -r requirements.txt
```

## How to Use
1. Generate the worksheet in pdf format with the following command:
```
python3 run.py --type [+|-|x|/|mix] --digits [1|2|3]
```
For addition only worksheet, use the following command:
```
python3 run.py --type +
```
For calculation up to 3 digit range, use the following command:
```
python3 run.py --digits 3
```

2. Print out the generated file `worksheet.pdf`

3. You can generate more questions by editing the parameter `total_question` under `run.py`

## Sample
[sample worksheet](sample-worksheet.pdf)

## Code Overview
Everything is written in python in `run.py`. You can play with the font and grid size with the variables under the `# Basic settings` section.

## Contributing
I appreciate all suggestions or PRs which will help kids learn math better. Feel free to fork the project and create a pull request with your idea.

## TODO
1. Add date/name/score section to the front page
2. Add support for Division ?
3. Pass in the number of questions with a flag (currently the default is 80)

## Special Thanks
My long time friend San for the inspiration of this project and lovely sons Tim and Hin. Thanks [thedanimal](https://github.com/thedanimal) for reviewing this README and adding new features.
