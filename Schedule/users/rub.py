pars = '((()))(())'

def balanced(pars):
    counter = 0
    for par in pars:
        if par == '(':
            counter += 1
        else:
            counter -= 1
        if counter < 0:
            return False

    return counter == 0

print(balanced(pars))

