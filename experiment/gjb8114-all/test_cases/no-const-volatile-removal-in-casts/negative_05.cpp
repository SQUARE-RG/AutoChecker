int main() {
    const volatile int value = 7;
    const volatile int* cvp = &value;
    const int* cp = const_cast<const int*>(cvp); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-5-2]
    return *cp;
}
