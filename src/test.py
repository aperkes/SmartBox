import cv2, time

caps = [0] * 4
for c in range(4):
    print('adding camera',str(c))
    caps[c] = cv2.VideoCapture(c * 2)
    caps[c].set(cv2.CAP_PROP_FPS,15)

print('reading frames...')
while True:
    for c in range(4):
        ret,frame = caps[c].read()
        if ret:
            cv2.imshow(str(c),frame)
    if cv2.waitKey(50) & 0xFF == ord('q'):
        break
for c in range(4):
    caps[c].release()
cv2.destroyAllWindows()
