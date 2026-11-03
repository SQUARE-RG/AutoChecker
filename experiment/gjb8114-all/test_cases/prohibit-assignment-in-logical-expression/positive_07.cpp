int main() {
    int values[3] = {1, 2, 3};
    int target = 2;
    int i = 0;
    while (i < 3 && values[i] != target) {
        ++i;
    }
    return 0;
}
