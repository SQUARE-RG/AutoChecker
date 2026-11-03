// Test: ordinary local variable in a for loop body block.
void accumulate(int limit) {
    int sum = 0;
    for (int i = 0; i < limit; ++i) {
        int value = i * 2;
        sum += value;
    }
    (void)sum;
}

int main() {
    accumulate(5);
    return 0;
}
