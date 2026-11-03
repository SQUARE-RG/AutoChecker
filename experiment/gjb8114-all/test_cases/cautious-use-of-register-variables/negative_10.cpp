// Test: register variable declared inside a try block.
void guarded_compute(int input) {
    int result = 0;
    try {
        register int temp = input + 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-13-2]
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
