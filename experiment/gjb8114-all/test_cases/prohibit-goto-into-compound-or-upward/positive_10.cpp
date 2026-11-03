int main() {
    int s = 0;
    for (int i = 0; i < 5; ++i) {
        if (i == 3) {
            goto next;
        }
        s += i;
    next:
        s += 2;
    }
    return s;
}
