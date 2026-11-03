int main() {
    const volatile int value = 9;
    const volatile int& cvr = value;
    volatile int& vr = const_cast<volatile int&>(cvr); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-5-2]
    vr = 10;
    return vr;
}
