#!/bin/zsh

# FILES=("${(@f)$(gsutil ls gs://jades-syllabi/syllabi)}")


# for f in ${FILES[@]}; do
#     python3 extract-document.py $f 'gs://jades-syllabi/interpreted-syllabi2/';
#     #echo $f;
#     #echo '';
# done

source venv/bin/activate;
pip install --upgrade -r requirements.txt;
python3 extract-document.py;
translate-texts.py;

