typedef const int* ConstIntPtr;

int main() {
    int value = 42;
    ConstIntPtr p = &value;
    int*& ref = const_cast<int*&>(p); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-5-2]
    (void)ref;
    return 0;
}
