nested_lst = []
for i in range(tree.BranchCount):
    branchList = tree.Branch(i)
    nested_lst.append(branchList)

for i_ in nested_lst:
    print i_
    print ''