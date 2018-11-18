import os

print("\t 1 minute load average is " + str(os.getloadavg()[0]))
print("\t 5 minute load average is " + str(os.getloadavg()[1]))
print("\t 15 minute load average is " + str(os.getloadavg()[2]))

