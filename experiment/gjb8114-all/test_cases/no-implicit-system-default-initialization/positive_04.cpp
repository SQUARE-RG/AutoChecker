int accumulate() {
    static int cache[4] = {1, 2, 3, 4};
    int sum = 0;
    for (int i = 0; i < 4; ++i) {
        sum += cache[i];
    }
    return sum;
}

int main() {
    return accumulate();
}
