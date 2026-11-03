int main() {
    try {
        throw 42;
    } catch (int value) {
        (void)value;
    }
    return 0;
}
