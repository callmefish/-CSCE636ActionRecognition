import os
import csv
import matplotlib.pyplot as plt


file1 = 'record/motion_res_3_100/opf_test.csv'

test_loss_3 = []
test_acc_3 = []
with open(file1, 'r') as f:
    reader = csv.reader(f)
    # 一行一行读取CSV文件，记录数值
    i = 0
    for row in reader:
        if i < 1:
            i += 1
            continue
        else:
            test_loss_3.append(round(float(row[2]), 6))
            test_acc_3.append(round(float(row[3])*0.01, 6))
f.close()

file2 = 'record/motion_res_3_100/opf_train.csv'
train_loss_3 = []
train_acc_3 = []
with open(file2, 'r') as f:
    reader = csv.reader(f)
    # 一行一行读取CSV文件，记录数值
    i = 0
    for row in reader:
        if i < 1:
            i += 1
            continue
        else:
            train_loss_3.append(round(float(row[3]), 6))
            train_acc_3.append(round(float(row[4])*0.01, 6))
f.close()

plt.figure()
plt.plot(train_loss_3, label='Training loss')
plt.plot(test_loss_3, label='Validation loss')
# plt.ylim(0, int(max(Loss)) + 1)
plt.title("opf Loss")
plt.xlabel("Epoch")
plt.ylabel("Loss")
plt.ylim(0, 10)
plt.legend()
# plt.savefig("opf Loss.png")
plt.show()

plt.figure()
plt.plot(train_acc_3, label='Training acc')
plt.plot(test_acc_3, label='Validation acc')
# plt.ylim(0, int(max(Loss)) + 1)
plt.title("opf Acc")
plt.xlabel("Epoch")
plt.ylabel("Acc")
plt.legend()
# plt.savefig("opf Acc.png")
plt.show()