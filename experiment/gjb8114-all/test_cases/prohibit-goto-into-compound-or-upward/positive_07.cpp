int main() {
    int i = 0;
    while (i < 5) {
        ++i;
        if (i == 3) {
            goto done;
        }
    }
done:
    return 0;
}
