def tree2nest(tree):
    nested_lst = []
    for i in range(tree.BranchCount):
        branchList = tree.Branch(i)
        nested_lst.append(branchList)
    return nested_lst

nested_lst = tree2nest(tree)
for i_ in nested_lst:
    print i_
    print ''