int main() {
    for (int i = 0; i < 3; ++i) {
        if (i == 2) {
            goto after_loop;
        }
    }
    after_loop:
    return 0;
}
