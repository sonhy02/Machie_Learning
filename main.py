list = [[1,2,3],[4,5,6],[7,8,9]]

row = len(list)
col = len(list[0])

result =  []
for c in range(col):
    for r in range(row):
        pixel = list[r][c]
        result.append(pixel)
print(result)