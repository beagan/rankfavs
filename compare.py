import math, operator
import ImageChops
import math, operator
from PIL import Image
import os
import time

def compare(file1, file2):
	image1 = Image.open(file1)
	image2 = Image.open(file2)
#	if image1.mode != "RGB":
#		image1 = image1.convert("RGB")
#	if image2.mode != "RGB":
#		image2 = image2.convert("RGB")
	#print image1
	#print image2
	image1 = image1.convert('L')
	image2 = image2.convert('L')
	h = ImageChops.difference(image1, image2).histogram()
	#print image1.size[0]
	#print image1.size[1]
    # calculate rms

	h1 = image1.histogram()
	h2 = image2.histogram()
	rms = math.sqrt(reduce(operator.add,
	    map(lambda a,b: (a-b)**2, h1, h2))/len(h1))
	return rms

import sys
t1= time.time()
for id in range(1,432):
	files = []
	for i in range(1,8):
		file = "/Users/Jason/person/" + str(id) + '/' + str(i) + ".jpg"
		if (os.path.isfile(file)):
			files.append(file)
	for x in files:
		for y in files:
			if not x == y and x<y:
				diff = compare(x, y)
				if diff < 400:
					print ("{} {} {}").format(x,y,diff)
					
t2 = time.time()
print t2-t1