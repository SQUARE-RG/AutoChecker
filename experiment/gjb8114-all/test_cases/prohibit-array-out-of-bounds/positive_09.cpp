int main() {
    constexpr int n = 4;
    int a[n] = {0};
    for (int i = 0; i < n - 1; ++i) {
        a[i + 1] = 0;
    }
    return 0;
}
