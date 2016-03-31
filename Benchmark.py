import subprocess as sp

target = open('bench.txt','w')
target.seek(0)
squareSize = 0

while(1):
	v = sp.check_output(['python', 'PathImg4Benchmark.py', 'images/katia.png', 'katia', '140', '3', '1', '0.1', str(squareSize)])
	print squareSize,v
	target.write('%s,%s' %(squareSize,v))
	squareSize += 1
