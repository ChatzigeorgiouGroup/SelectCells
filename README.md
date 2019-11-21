# Click Notochord Cells
An application to annotate Notochord cell locations 

### Getting started

### controls
`left click` adds a location.
`right click` removes a location

<kbd>enter</kbd> saves the results to ./cell_locations/{filename}/ where it will place the image as a png and the locations as a pickled dictionary.
<kbd>left</kbd> and <kbd>right</kbd> open next/previous images from the loaded list
<kbd>+</kbd> and <kbd>-<kbd> increment and decrement the cell number so that you can skip numbers you are unsure about and annotate the cells with exactly the numbers you want.
<kbd>1</kbd> applies a gaussian filter on the image
<kbd>2</kbd> adjusts the gamma with gamma=0.9
<kbd>3</kbd> adjuts the gamma with gamma=1.1
<kbd>r</kbd> resets all results and editing for the current image
