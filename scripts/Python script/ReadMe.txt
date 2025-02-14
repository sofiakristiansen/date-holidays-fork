This is the script to edit each countries .yaml file.

It finds lines with "en: ", checks for a Wikipedia article, then checks for the Swedish article and adds a new line "sv: " with the exact title of the Swedish page.



Usage: 
1. Install Python
2. Place all .yaml files that are to be processed in a zip file called "input_files.zip".
3. In bash in this directory, enter "python script.py".
4. Behold the script doing it's thing, this will likely take a while if there are many countries in the zip.
5. When it's done it will output updated .yaml files in "updated_files.zip".
6. You can then copy those files into the existing structure as you see fit.


Ps. Script was created by ChatGPT, so it might be suboptimal and incorrect, who knows...