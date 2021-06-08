# def slotWheels(history):

history = ['137', '364', '115', '724']

total = 0
num_list = []
for i in range(len(history)):
    his_list = list(history[i])
    his_list.sort()
    num_list.append(his_list)
print(num_list)

size_wheel = len(history[0])
size_spin = len(history)
for k in range(size_wheel):
    max_value = 0
    for i in range(size_spin):
        for j in range(len(num_list[i])):
            if int(num_list[i][j]) >= max_value:
                max_value = int(num_list[i][j])
        if len(num_list[i]):
            num_list[i].pop()
    total = total + max_value
    print(num_list)
    print(max_value)
print(total)