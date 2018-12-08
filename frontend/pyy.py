from matplotlib import pyplot as plt
from matplotlib import style
import numpy as np

style.use('ggplot')

x,y = np.loadtxt('/var/lib/collectd/csv/e74a0b35873c/cpu-0/cpu-system-2018-12-07', unpack = True, delimiter = ',', skiprows=1 )


plt.plot(x, y)
plt.savefig('my_NS_LB11')

#print x
#print y

