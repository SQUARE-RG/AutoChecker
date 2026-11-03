// Test: ordinary local variable declared inside a try block.
void guarded_compute(int input) {
    int result = 0;
    try {
        int temp = input + 1;
        result = temp;
    } catch (int) {
        result = -1;
    }
    (void)result;
}

int main() {
    guarded_compute(3);
    return 0;
}
