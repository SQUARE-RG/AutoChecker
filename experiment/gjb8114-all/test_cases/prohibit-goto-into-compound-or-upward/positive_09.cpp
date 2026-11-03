int main() {
    int i = 0;
    while (i < 5) {
        ++i;
        goto done;
    }
done:
    return i;
}
