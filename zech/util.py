from __future__ import print_function, unicode_literals

from os import listdir, remove, rmdir, makedirs
from os.path import isfile, isdir, join
from numpy import concatenate, linspace
import matplotlib
import errno


def delete_dir(d):
    ''' Deletes a directory and its content recursively.
    '''
    for name in listdir(d):
        fp = join(d, name)
        if not isfile(fp) and isdir(fp):
            # It's another directory - recurse in to it...
            delete_dir(fp)
        else:
            # It's a file - remove it...
            remove(fp)
    rmdir(d)


def make_dir(path):
    '''Create directories.

    Equivalent to 'mkdir -p'
    '''
    try:
        makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and isdir(path):
            pass
        else:
            raise


def flatten(x):
    """Flatten any sequence to a flat list.

    Returns a single, flat list which contains all elements retrieved
    from the sequence and all recursively contained sub-sequences
    (iterables).

    Examples:
    >>> flatten([1, 2, [3,4], (5,6)])
    [1, 2, 3, 4, 5, 6]
    >>> flatten([[[1,2,3], (42,None)], [4,5], [6], 7, MyVector(8,9,10)])
    [1, 2, 3, 42, None, 4, 5, 6, 7, 8, 9, 10]
    """

    result = []
    for el in x:
        # if isinstance(el, (list, tuple)):
        if hasattr(el, "__iter__") and not isinstance(el, basestring):
            result.extend(flatten(el))
        else:
            result.append(el)
    return result


def yes_or_no(message="Yes or No? "):
    '''Prompt to answer 'yes' or 'no'.
    '''
    while True:
        try:
            reply = raw_input(message)
        except EOFError:
            print
            continue
        reply = reply.strip().lower()
        if reply in ('y', 'yes'):
            return True
        elif reply in ('n', 'no'):
            return False
        else:
            continue


def traverse(o, tree_types=(list, tuple)):
    # borrowed from:
    # http://stackoverflow.com/questions/6340351/python-iterating-through-list-of-list
    if isinstance(o, tree_types):
        for value in o:
            for subvalue in traverse(value):
                yield subvalue
    else:
        yield o


def parse_function_call(expr):
    '''Parse a string similar to a function call.

    Examples
    --------
    >>> l = 'complement(join(97999..98793,69611..69724))'
    >>> parse_function_call(l)
    '''
    def parser(iter):
        items = []
        item = ''
        for char in iter:
            if char.isspace():
                continue
            if char in '(),' and item:
                items.append(item)
                item = ''
            if char == '(':
                result, close_paren = parser(iter)
                if not close_paren:
                    raise ValueError("Unbalanced parentheses")
                items.append(result)
            elif char == ')':
                return items, True
            elif char != ',':
                item += char
        if item:
            items.append(item)
        return items, False
    return parser(iter(expr))[0]


def cmap_discretize(cmap, N):
    """Return a discrete colormap from the continuous colormap cmap.

    Parameters
    ----------
    cmap : colormap instance, eg. cm.jet.
    N : number of colors.

    Examples
    --------
    >>> x = resize(arange(100), (5,100))
    >>> djet = cmap_discretize(cm.jet, 5)
    >>> imshow(x, cmap=djet)
    """
    colors_i = concatenate((linspace(0, 1., N), (0.,0.,0.,0.)))
    colors_rgba = cmap(colors_i)
    indices = linspace(0, 1., N+1)
    cdict = {}
    for ki,key in enumerate(('red','green','blue')):
        cdict[key] = [(indices[i], colors_rgba[i-1,ki], colors_rgba[i,ki]) for i in xrange(N+1)]
    # Return colormap object.
    return matplotlib.colors.LinearSegmentedColormap(cmap.name + "_%d"%N, cdict, 1024)