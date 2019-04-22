"""
Convert a mmSolver log file into an image.
"""

import argparse
import glob
import os

import matplotlib.pyplot as plt


def generate_plot_error_per_iteration(data, ax):
    x = []
    y_avg = []
    y_errors = []
    for it_k, it_v in data.iteritems():
        if it_v['type'] != 'normal':
            continue
        x.append(it_v['number'])
        for i, e in enumerate(it_v['error']):
            if len(y_errors) < (i + 1):
                y_errors.append([])
            y_errors[i].append(e)

    x_errors = [x] * len(y_errors)
    args = zip(x_errors, y_errors)
    xargs = []
    for a in args:
        xargs.append(a[0])
        xargs.append(a[-1])
    ax.set_title('Error All')
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Errors')
    ax.plot(*xargs)
    ax.grid(True)
    return ax


def generate_plot_error_min_avg_max(data, ax):
    x = []
    y_min = []
    y_avg = []
    y_max = []
    for it_k, it_v in data.iteritems():
        if it_v['type'] != 'normal':
            continue
        x.append(it_v['number'])
        y_min.append(it_v['error_min'])
        y_avg.append(it_v['error_avg'])
        y_max.append(it_v['error_max'])

    ax.set_title('Error Min/Avg/Max')
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Errors')
    ax.plot(
        x, y_min,
        x, y_avg,
        x, y_max)
    ax.grid(True)
    return ax


def generate_plot_value_dots(data, ax):
    x_parm = []
    y_parm = []
    color = []
    size = []
    it_num_max = 1
    for it_k, it_v in data.iteritems():
        if it_v['type'] != 'normal':
            continue
        it_num_max = it_v['number']
    for it_k, it_v in data.iteritems():
        if it_v['type'] != 'normal':
            continue
        it_num = it_v['number']
        for i, v in enumerate(it_v['parm']):
            x_parm.append(i)
            y_parm.append(v)
            color.append(it_num)
            s = 0.5 * ((float(it_num) / float(it_num_max)) * 0.5)
            size.append((s * 12.0) ** 2)

    ax.set_title('Parameter Values')
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Values')
    ax.scatter(
        x_parm, y_parm,
        c=color,
        s=size
    )
    ax.grid(True)
    return ax


def generate_plot_value_lines(data, ax):
    x_parm = []
    y_parm = []
    it_num_max = 1
    for it_k, it_v in data.iteritems():
        if it_v['type'] != 'normal':
            continue
        it_num_max = it_v['number']
    for it_k, it_v in data.iteritems():
        if it_v['type'] != 'normal':
            continue
        it_num = it_v['number']
        s = (float(it_num) / float(it_num_max)) - (1.0 / float(it_num_max))
        s = (s - 0.5)
        for i, v in enumerate(it_v['parm']):
            if len(x_parm) < (i + 1):
                x_parm.append([])
            if len(y_parm) < (i + 1):
                y_parm.append([])
            x_parm[i].append(float(i) + s)
            y_parm[i].append(v)

    args = zip(x_parm, y_parm)
    xargs = []
    for a in args:
        xargs.append(a[0])
        xargs.append(a[-1])

    ax.set_title('Parameter Values')
    ax.set_xlabel('Iteration')
    ax.set_ylabel('Values')
    ax.plot(*xargs)
    ax.grid(True)
    return ax


def read_log(file_path):
    data = {}
    print 'file_path:', repr(file_path)
    with open(file_path, 'r') as f:
        it_key_fmt = 'iter_%s_%s'
        it_key = 'iter_s_s'

        for line in f:
            name = 'iteration '
            if line.startswith(name):
                line = line[len(name):]
                it_type = str(line.split(':')[0])
                it_num = int(line.split(':')[-1])
                it_key = it_key_fmt % (it_type, str(it_num).zfill(8))
                data[it_key] = {
                    'type': it_type,
                    'number': it_num,
                    'parm': [],
                    'error': [],
                    'error_min': None,
                    'error_max': None,
                    'error_avg': None,
                }

            name = 'i='
            if line.startswith(name):
                splt = line.split(' ')
                parm_num = splt[0]
                parm_val = splt[-1]
                parm_num = int(parm_num.split('=')[-1])
                parm_val = float(parm_val.split('=')[-1])
                data[it_key]['parm'].append(parm_val)

            name = 'error dist '
            if line.startswith(name):
                line = line[len(name):]
                err_num = line.split(' ')[0]
                err_val = line.split(' ')[-1]
                err_num = int(err_num.split('=')[-1])
                err_val = float(err_val.split('=')[-1])
                data[it_key]['error'].append(err_val)

            name = 'emin='
            if line.startswith(name):
                err_min = line.split(' ')[0]
                err_max = line.split(' ')[1]
                err_avg = line.split(' ')[2]
                err_min = float(err_min.split('=')[-1])
                err_max = float(err_max.split('=')[-1])
                err_avg = float(err_avg.split('=')[-1])
                data[it_key]['error_min'] = err_min
                data[it_key]['error_max'] = err_max
                data[it_key]['error_avg'] = err_avg
    return data


def read_flags(file_path):
    print 'file_path:', repr(file_path)
    return


def main(file_paths):
    paths = []
    for file_path in file_paths:
        file_path = os.path.abspath(file_path)
        paths += glob.glob(file_path)

    for file_path in paths:
        head, ext = os.path.splitext(file_path)
        data = read_log(file_path)
        if len(data) == 0:
            continue

        fig, ax = plt.subplots(2, 2, dpi=600)

        ax[0][0] = generate_plot_error_min_avg_max(data, ax[0][0])
        ax[0][1] = generate_plot_error_per_iteration(data, ax[0][1])
        ax[1][0] = generate_plot_value_lines(data, ax[1][0])
        ax[1][1] = generate_plot_value_dots(data, ax[1][1])

        fig.tight_layout()
        fig.savefig(head + '.png')
        plt.close(fig)
    return


def parse():
    text = 'Create an image from debug mmSolver data logs..'
    parser = argparse.ArgumentParser(description=text)
    parser.add_argument(
        'files',
        metavar='FILE',
        type=str,
        nargs='+',
        help='Input file'
    )
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    args = parse()
    main(args.files)
