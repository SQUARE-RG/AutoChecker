using ConstInt = int const; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-9-2]

int main() {
    ConstInt value = 1;
    (void)value;
    return 0;
}
