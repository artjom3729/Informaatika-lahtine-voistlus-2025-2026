# sisendi lugemine:
s = input()      # loeme sisendist ühe rea
a, b = s.split() # poolitame selle tühiku kohalt
a = int(a)       # teisendame esimese poole arvuks
b = int(b)       # teisendame teise poole arvuks

# eelmised neli rida võiks asenda ka ühega:
# a, b = [int(x) for x in input().split()]

# aga kindlasti ei või sisendit lugeda nii (vt https://eio.ee/KKK/StdIO):
# s = input('Sisesta kaks arvu')

# sisendit ei või lugeda ka ka nii (vt https://eio.ee/KKK/StdIO):
# a = input()
# b = input()

# leiame vastuse:
vastus = a + b

# väljastame vastuse:
print(vastus)

# vastust ei tohi väljastada nii (vt https://eio.ee/KKK/StdIO):
# print('Summa on', vastus)