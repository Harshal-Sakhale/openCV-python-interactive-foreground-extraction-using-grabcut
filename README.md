# openCV-python-interactive-foreground-extraction-using-grabcut
OpenCV python based interactive image foreground extraction

Interactive user input using simple keystrokes and mouse gestures to draw touchup curves to define foreground, background, obvious background, probable foreground/background, etc.

Possible to increase/decrease brush thickness.

Possible to change the background (by pressing 'x') in the output to clearly verify if any part of foreground is not accidentally segmented as background.

Possible to generate output image with transparent background with foreground extracted.

First the user draws a blue rectangle to mark ROI which clearly includes all parts of the object to be identified as foreground.

Then presses 'n' to apply grabcut multiple number of times.

If not satistied with the result user can draw touchup curves indicating foreground, background, etc. and again apply gragbcut algorithm using key 'n'.

Possible to view large images on small screens by scaling the entire image and also displaying a small part of the image unscaled on which user wishes to draw touchup curves indicated by yellow box within the blue rectangle in a separate window.

Very user friendly (fast learning curve) and displays all options inteactively on the cosole.
