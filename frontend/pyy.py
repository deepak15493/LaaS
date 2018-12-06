from matplotlib import pyplot as plt
from matplotlib import style
import numpy as np

style.use('ggplot')

x,y = np.loadtxt('/var/lib/collectd/csv/258332e14d2a/cpu-0/cpu-idle-2018-12-05', unpack = True, delimiter = ',', skiprows=1 )


plt.plot(x, y)
plt.savefig('sahil')
#print x
#print y

