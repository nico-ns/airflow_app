from  _cache import Cache, CacheChecker
from time import sleep


x = Cache()
y = CacheChecker(x.is_it_time_to_dump, 6)
x[1] = "lhbscpv"
i = 0
while True:
	sleep(1)
	i += 1
	if i == 1:
		x[2] = "jbvs"
	if i == 3:
		print(x)
	if i == 10:
		print(x)
	if i == 15:
		x[6] = 7
	if i == 20:
		print(x)
	if i == 40:
		print(x)

print(x.__dict__)
print(x[1])
x.dump_to_file()