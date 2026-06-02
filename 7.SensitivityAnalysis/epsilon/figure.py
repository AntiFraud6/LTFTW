import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator
import numpy as np

# 设置全局字体为Times New Roman（SCI常用）
plt.rcParams['font.family'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.size'] = 12
plt.rcParams['axes.linewidth'] = 1.5

# 数据（现在包含5列：epsilon, EarlyWarn1, EarlyWarn2, F1, FPR）
data = [
    [0.001, 0.39, 3.46, 0.8364, 0.1439],
    [0.005, 1.55, 4.08, 0.8465, 0.1512],
    [0.010, 1.93, 4.31, 0.8529, 0.1437],
    [0.015, 2.46, 4.38, 0.8514, 0.1460],
    [0.020, 2.48, 4.36, 0.8498, 0.1508],
    [0.025, 2.46, 4.45, 0.8546, 0.1437],
    [0.030, 2.36, 4.26, 0.8509, 0.1457],
    [0.035, 1.98, 4.21, 0.8516, 0.1451],
    [0.040, 2.03, 4.15, 0.8503, 0.1453],
    [0.045, 2.17, 4.29, 0.8469, 0.1451],
    [0.050, 1.92, 4.35, 0.8426, 0.1503]
]

eps = [row[0] for row in data]
early_warn1 = [row[1] for row in data]   # 原 EarlyWarn
early_warn2 = [row[2] for row in data]   # 新增 EarlyWarn2
f1 = [row[3] for row in data]
fpr = [row[4] for row in data]

# 创建画布（设置合适的尺寸比例）
fig, ax1 = plt.subplots(figsize=(8, 6), dpi=300)

# 设置SCI风格配色（色盲友好，新加一种颜色用于 EarlyWarn2）
colors = {
    'f1': '#f3cfa9',      # 深蓝
    'fpr': '#b6bcd4',     # 绿色
    'early1': '#7a92b0',  # 红色（EarlyWarn1）
    'early2': '#d4826c'   # 橙色（EarlyWarn2，新增）
}

# 绘制主坐标轴曲线
line1, = ax1.plot(eps, f1, color=colors['f1'], linewidth=2.5,
                 marker='o', markersize=8, markeredgewidth=1.5,
                 markerfacecolor='white', markeredgecolor=colors['f1'],
                 label='F1 Score')
line2, = ax1.plot(eps, fpr, color=colors['fpr'], linewidth=2.5,
                 linestyle='--', marker='s', markersize=8,
                 markeredgewidth=1.5, markerfacecolor='white',
                 markeredgecolor=colors['fpr'], label='FPR')

# 创建次坐标轴
ax2 = ax1.twinx()
line3, = ax2.plot(eps, early_warn1, color=colors['early1'], linewidth=2.5,
                 marker='^', markersize=8, markeredgewidth=1.5,
                 markerfacecolor='white', markeredgecolor=colors['early1'],
                 label='MLLT')   # 标签更新为 EarlyWarn1

line4, = ax2.plot(eps, early_warn2, color=colors['early2'], linewidth=2.5,
                 linestyle='-.', marker='D', markersize=8,
                 markeredgewidth=1.5, markerfacecolor='white',
                 markeredgecolor=colors['early2'],
                 label='MAWO')   # 新增 EarlyWarn2 曲线

# 设置坐标轴标签
ax1.set_xlabel(r'$\epsilon$', fontsize=14, fontweight='bold')
ax1.set_ylabel('F1 Score / FPR', fontsize=14, fontweight='bold', color='k')
ax2.set_ylabel('MLLT/MAWO', fontsize=14, fontweight='bold', color='k')

# 设置刻度
ax1.xaxis.set_major_locator(MultipleLocator(0.01))
ax1.yaxis.set_major_locator(MultipleLocator(0.2))
ax2.yaxis.set_major_locator(MultipleLocator(5))

# 设置坐标轴范围
ax1.set_xlim(-0.003, 0.055)
ax1.set_ylim(-0.00, 1.10)
ax2.set_ylim(-10.0, 10.0)

# 设置刻度朝内
ax1.tick_params(direction='in', width=1.5, length=6, labelsize=12)
ax2.tick_params(direction='in', width=1.5, length=6, labelsize=12)

# 合并图例（放在右上角，无边框）
lines = [line1, line2, line3, line4]
labels = ['F1 Score', 'FPR', 'MLLT', 'MAWO']
ax1.legend(lines, labels, loc='upper right', frameon=False,
           fontsize=12, ncol=1)

# 调整布局
plt.tight_layout()

# 保存为高分辨率图片（用于论文）
plt.savefig('metrics_vs_epsilon_sci.png', dpi=600, bbox_inches='tight',
            facecolor='white', edgecolor='none')
plt.savefig('metrics_vs_epsilon_sci.pdf', format='pdf', bbox_inches='tight')

plt.close()





# import matplotlib.pyplot as plt
# from matplotlib.ticker import MultipleLocator
# import numpy as np
#
# # 设置全局字体（兼容中文与英文）
# plt.rcParams['font.family'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
# plt.rcParams['axes.unicode_minus'] = False
# plt.rcParams['font.size'] = 12
# plt.rcParams['axes.linewidth'] = 1.5
#
# # 数据（X 轴为字符串标签）
# labels = ["0.4+0.4", "0.5+0.2", "0.5+0.5", "0.6+0.3", "25th", "50th", "75th", "mean"]
# early_warn = [0.44, 0.35, -0.08, 0.33, 0.66, 0.39, -0.53, -0.12]
# f1 = [0.8319, 0.8535, 0.8234, 0.8467, 0.8622, 0.8364, 0.8000, 0.8163]
# fpr = [0.1476, 0.1371, 0.1441, 0.1406, 0.1275, 0.1439, 0.1233, 0.1443]
# early_warn2 = [3.53, 3.55, 3.14, 3.29, 3.85, 3.46, 3.39, 3.06]
#
# x = np.arange(len(labels))  # 用整数位置表示分类
#
# # 创建画布
# fig, ax1 = plt.subplots(figsize=(8, 6), dpi=300)
#
# # SCI 风格配色（增加一种颜色用于 EarlyWarn2）
# colors = {
#     'f1': '#f3cfa9',
#     'fpr': '#b6bcd4',
#     'early1': '#7a92b0',   # 原 Early Warning
#     'early2': '#d4826c'    # 新增 EarlyWarn2
# }
#
# # 主坐标轴：F1 和 FPR
# line1, = ax1.plot(x, f1, color=colors['f1'], linewidth=2.5,
#                   marker='o', markersize=8, markeredgewidth=1.5,
#                   markerfacecolor='white', markeredgecolor=colors['f1'],
#                   label='F1 Score')
# line2, = ax1.plot(x, fpr, color=colors['fpr'], linewidth=2.5,
#                   linestyle='--', marker='s', markersize=8,
#                   markeredgewidth=1.5, markerfacecolor='white',
#                   markeredgecolor=colors['fpr'], label='FPR')
#
# # 次坐标轴：EarlyWarn1 与 EarlyWarn2
# ax2 = ax1.twinx()
# line3, = ax2.plot(x, early_warn, color=colors['early1'], linewidth=2.5,
#                   marker='^', markersize=8, markeredgewidth=1.5,
#                   markerfacecolor='white', markeredgecolor=colors['early1'],
#                   label='MLLT')        # 原 Early Warning → EarlyWarn1
#
# line4, = ax2.plot(x, early_warn2, color=colors['early2'], linewidth=2.5,
#                   linestyle='-.', marker='D', markersize=8,
#                   markeredgewidth=1.5, markerfacecolor='white',
#                   markeredgecolor=colors['early2'],
#                   label='MAWO')        # 新增 EarlyWarn2 曲线
#
# # 坐标轴标签
# ax1.set_xlabel('Configuration', fontsize=14, fontweight='bold')
# ax1.set_ylabel('F1 Score / FPR', fontsize=14, fontweight='bold', color='k')
# ax2.set_ylabel('MLLT/MAWO', fontsize=14, fontweight='bold', color='k')
#
# # 设置 X 轴刻度标签
# ax1.set_xticks(x)
# ax1.set_xticklabels(labels, rotation=45, ha='right')
#
# # 设置 Y 轴范围
# ax1.set_ylim(-0.10, 1.10)
# ax2.set_ylim(-10.0, 10.0)   # 足够包含 EarlyWarn1 和 EarlyWarn2
# ax2.yaxis.set_major_locator(MultipleLocator(5))
#
# # 刻度朝内
# ax1.tick_params(direction='in', width=1.5, length=6, labelsize=12)
# ax2.tick_params(direction='in', width=1.5, length=6, labelsize=12)
#
# # 合并图例
# lines = [line1, line2, line3, line4]
# labels_legend = ['F1 Score', 'FPR', 'MLLT', 'MAWO']
# ax1.legend(lines, labels_legend, loc='upper right', frameon=False,
#            fontsize=12, ncol=1)
#
# # 布局与保存
# plt.tight_layout()
# plt.savefig('metrics_vs_config_sci.png', dpi=600, bbox_inches='tight',
#             facecolor='white', edgecolor='none')
# plt.savefig('metrics_vs_config_sci.pdf', format='pdf', bbox_inches='tight')
# plt.close()





