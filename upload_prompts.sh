#upload prompts
cp flashcard*.json /home/erik/flashcards/
scp *.prompt erik@chinese.eriktamm.com:/opt/prompts_to_process
scp /home/erik/flashcards/* erik@chinese.eriktamm.com:/var/www/html/flashcards
rm *.prompt


