int add_ints(int left, int right) { return left + right; }
int sub_ints(int left, int right) { return left - right; }

int (*choose(bool add))(int, int) { return add ? &add_ints : &sub_ints; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-1]

int main() {
    return choose(true)(7, 2);
}
